#!/usr/bin/env python3
"""Allocate global release numbers on a separately protected Git registry branch.

No firmware is built, signed, published or programmed here. Registry commits are
made only in temporary checkouts; normal fast-forward push is the concurrency
boundary. A failed/ambiguous push must be reconciled by request ID before retry.
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import uuid

LIMITS = {"firmware": (1 << 20) - 1, "bootloader": (1 << 12) - 1}
FLOORS = {"firmware": 8, "bootloader": 5}
SEED = pathlib.Path(__file__).resolve().parents[1] / "registry-seed.json"
RECORD_FIELDS = {"schemaVersion", "requestId", "component", "number", "sourceDigest", "actor", "actorId", "createdAt"}


class AllocationError(ValueError):
    pass


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise AllocationError("Duplicate JSON field")
        result[key] = value
    return result


def read_json(path):
    if path.is_symlink() or not path.is_file():
        raise AllocationError("Registry JSON must be a regular file")
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_object)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise AllocationError("Invalid registry JSON") from error


def _integer(value, low, high):
    return type(value) is int and low <= value <= high


def validate_request(request_id, component, source_digest, actor, actor_id):
    try:
        parsed = uuid.UUID(request_id)
        canonical = str(parsed)
    except (ValueError, TypeError, AttributeError) as error:
        raise AllocationError("requestId must be a canonical UUID4") from error
    if request_id != canonical or parsed.version != 4:
        raise AllocationError("requestId must be a canonical UUID4")
    if not isinstance(component, str) or component not in LIMITS:
        raise AllocationError("Unknown component")
    if not isinstance(source_digest, str) or not re.fullmatch(r"[0-9a-f]{64}", source_digest):
        raise AllocationError("sourceDigest must be a lowercase SHA-256")
    if not isinstance(actor, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*(?:\[bot\])?", actor):
        raise AllocationError("actor must be a GitHub login")
    if not isinstance(actor_id, str) or not re.fullmatch(r"[1-9][0-9]{0,63}", actor_id):
        raise AllocationError("actorId must be a positive decimal string")


def _validate_state(state):
    if not isinstance(state, dict) or set(state) != {"schemaVersion", "counters", "reservedThrough"}:
        raise AllocationError("Invalid registry state fields")
    if type(state["schemaVersion"]) is not int or state["schemaVersion"] != 1:
        raise AllocationError("Unsupported registry schema")
    if not isinstance(state["reservedThrough"], dict) or set(state["reservedThrough"]) != set(FLOORS):
        raise AllocationError("Invalid reservedThrough fields")
    for component, floor in FLOORS.items():
        if type(state["reservedThrough"][component]) is not int or state["reservedThrough"][component] != floor:
            raise AllocationError("Legacy reservation floors cannot change")
    counters = state["counters"]
    if not isinstance(counters, dict) or set(counters) != set(LIMITS):
        raise AllocationError("Invalid counter fields")
    for component, limit in LIMITS.items():
        if not _integer(counters[component], FLOORS[component], limit):
            raise AllocationError("Counter outside component bounds")
    return counters


def validate_registry(state, records):
    counters = _validate_state(state)
    if not isinstance(records, dict):
        raise AllocationError("Invalid request records")
    numbers = {component: set() for component in LIMITS}
    for request_id, record in records.items():
        if not isinstance(record, dict) or set(record) != RECORD_FIELDS:
            raise AllocationError("Invalid request record fields")
        if type(record["schemaVersion"]) is not int or record["schemaVersion"] != 1:
            raise AllocationError("Unsupported request schema")
        validate_request(record["requestId"], record["component"], record["sourceDigest"], record["actor"], record["actorId"])
        if request_id != record["requestId"]:
            raise AllocationError("Request filename and requestId differ")
        component, number = record["component"], record["number"]
        if not _integer(number, FLOORS[component] + 1, counters[component]):
            raise AllocationError("Request number outside allocated range")
        if number in numbers[component]:
            raise AllocationError("Duplicate component number")
        numbers[component].add(number)
        date = record["createdAt"]
        if not isinstance(date, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", date):
            raise AllocationError("createdAt must be a UTC timestamp")
        try:
            datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError as error:
            raise AllocationError("Invalid createdAt date") from error
    for component, allocated in numbers.items():
        if len(allocated) != counters[component] - FLOORS[component]:
            raise AllocationError("Registry history is incomplete; numbers cannot be removed")
    return state, records


def load_registry(directory):
    directory = pathlib.Path(directory)
    if directory.is_symlink() or not directory.is_dir():
        raise AllocationError("Registry directory is unavailable")
    if any(path.name not in {".git", "state.json", "requests"} for path in directory.iterdir()):
        raise AllocationError("Unexpected registry entry")
    state = read_json(directory / "state.json")
    requests = directory / "requests"
    records = {}
    if requests.is_symlink() or (requests.exists() and not requests.is_dir()):
        raise AllocationError("requests must be a directory")
    if requests.exists():
        for path in requests.iterdir():
            if path.suffix != ".json":
                raise AllocationError("Unexpected request entry")
            records[path.stem] = read_json(path)
    return validate_registry(state, records)


def _write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def initialize(directory, seed=SEED):
    directory = pathlib.Path(directory)
    if directory.is_symlink() or (directory.exists() and (not directory.is_dir() or any(directory.iterdir()))):
        raise AllocationError("init requires a new or empty directory; never reset a registry")
    state = read_json(pathlib.Path(seed))
    validate_registry(state, {})
    directory.mkdir(parents=True, exist_ok=True)
    _write_json(directory / "state.json", state)
    return state


def lookup_request(state, records, request_id):
    validate_registry(state, records)
    # Validate the UUID even if no record exists.
    validate_request(request_id, "firmware", "0" * 64, "lookup", "1")
    return records.get(request_id)


def _existing(records, request_id, component, source_digest, actor_id):
    record = records.get(request_id)
    if record is not None and (record["component"], record["sourceDigest"], record["actorId"]) != (component, source_digest, actor_id):
        raise AllocationError("requestId was already used with different component, sourceDigest or actorId")
    return record


def _git(directory, *args, check=True, input=None, binary=False):
    try:
        result = subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "-c", "core.fsmonitor=false", *args],
                                cwd=directory, capture_output=True, text=not binary, input=input, timeout=60)
    except (OSError, UnicodeError, subprocess.TimeoutExpired) as error:
        raise AllocationError("Git operation unavailable or timed out; retry with the same requestId") from error
    if check and result.returncode:
        # Never print transport diagnostics: remote URLs/config can contain credentials.
        raise AllocationError("Git operation failed; check access/registry branch and retry with the same requestId")
    return result


def validate_git_history(directory, state, records):
    """Check all reachable transitions, including coherent fast-forward rollback.

    Registry history is a linear seed followed by one reservation per commit.
    Batch both the change list and state blobs, avoiding Git calls per record.
    Ref deletion/force-push protection is still required on the remote: a new
    client cannot prove that an entire replaced history once existed elsewhere.
    """
    if _git(directory, "rev-parse", "--is-shallow-repository").stdout.strip() != "false":
        raise AllocationError("Complete registry history is required; shallow history is rejected")
    log = _git(directory, "log", "--reverse", "--topo-order", "--no-show-signature", "--no-color",
               "--format=commit %H %P", "--name-status", "--no-renames", "--root", "HEAD").stdout
    commits = []
    for line in log.splitlines():
        if line.startswith("commit "):
            fields = line.split()
            if len(fields) not in (2, 3) or any(not re.fullmatch(r"[0-9a-f]{40,64}", value) for value in fields[1:]):
                raise AllocationError("Registry history must be linear; merges are rejected")
            expected_parents = [commits[-1][0]] if commits else []
            if fields[2:] != expected_parents:
                raise AllocationError("Registry history must have one complete linear ancestry")
            commits.append((fields[1], []))
        elif line:
            if not commits:
                raise AllocationError("Invalid registry history")
            commits[-1][1].append(line)
    if not commits:
        raise AllocationError("Registry history is missing")
    queries = "".join(commit + ":state.json\n" for commit, _ in commits).encode("ascii")
    blobs = _git(directory, "cat-file", "--batch", input=queries, binary=True).stdout
    offset, expected_counters, seen = 0, dict(FLOORS), set()
    for index, (_, changes) in enumerate(commits):
        if index == 0:
            if changes != ["A\tstate.json"]:
                raise AllocationError("Registry root must contain only the original seed state")
        else:
            additions = [line[2:] for line in changes if line.startswith("A\trequests/")]
            if len(changes) != 2 or changes.count("M\tstate.json") != 1 or len(additions) != 1:
                raise AllocationError("Registry history must only append one request and increment its counter")
            path = pathlib.PurePosixPath(additions[0])
            request_id = path.stem
            if str(path) != "requests/" + request_id + ".json" or request_id not in records or request_id in seen:
                raise AllocationError("Registry history removed, replaced or reused a request")
            record = records[request_id]
            component = record["component"]
            expected_counters[component] += 1
            if record["number"] != expected_counters[component]:
                raise AllocationError("Registry history skipped or reused a component number")
            seen.add(request_id)
        header_end = blobs.find(b"\n", offset)
        header = blobs[offset:header_end].split()
        if header_end < 0 or len(header) != 3 or header[1] != b"blob" or not header[2].isdigit():
            raise AllocationError("Registry history state is missing")
        start, size = header_end + 1, int(header[2])
        offset = start + size + 1
        if blobs[offset - 1:offset] != b"\n":
            raise AllocationError("Invalid registry history state")
        try:
            historical_state = json.loads(blobs[start:start + size].decode("utf-8"), object_pairs_hook=_object)
        except (UnicodeError, json.JSONDecodeError) as error:
            raise AllocationError("Invalid registry history JSON") from error
        if _validate_state(historical_state) != expected_counters:
            raise AllocationError("Registry history counters must increase exactly once per reservation")
    if offset != len(blobs) or expected_counters != state["counters"] or seen != set(records):
        raise AllocationError("Registry history does not match its current state")


def _refresh(directory, branch):
    # A missing branch is an error. No code path creates it or reuses the seed.
    _git(directory, "fetch", "--quiet", "--no-tags", "origin", "refs/heads/" + branch)
    _git(directory, "checkout", "--quiet", "--detach", "FETCH_HEAD")
    state, records = load_registry(directory)
    validate_git_history(directory, state, records)
    return state, records


def reserve(*, remote, branch="registry", request_id, component, source_digest, actor, actor_id, max_attempts=8):
    validate_request(request_id, component, source_digest, actor, actor_id)
    if not _integer(max_attempts, 1, 32):
        raise AllocationError("max_attempts must be 1..32")
    if not isinstance(branch, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,127}", branch) or any(
            part.startswith(".") or part.endswith((".", ".lock")) or not part for part in branch.split("/")) or ".." in branch:
        raise AllocationError("Invalid registry branch name")
    if not isinstance(remote, str) or not remote or remote.startswith("-"):
        raise AllocationError("Invalid remote")
    if pathlib.Path(remote).exists():
        remote = str(pathlib.Path(remote).resolve())
    with tempfile.TemporaryDirectory(prefix="release-numbers-") as temporary:
        directory = pathlib.Path(temporary)
        _git(directory, "init", "--quiet")
        _git(directory, "remote", "add", "origin", remote)
        for _ in range(max_attempts):
            state, records = _refresh(directory, branch)
            prior = _existing(records, request_id, component, source_digest, actor_id)
            if prior is not None:
                return prior
            number = state["counters"][component] + 1
            if number > LIMITS[component]:
                raise AllocationError("Component number space exhausted; never wrap or reuse numbers")
            record = dict(schemaVersion=1, requestId=request_id, component=component, number=number,
                          sourceDigest=source_digest, actor=actor, actorId=actor_id,
                          createdAt=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
            state["counters"][component] = number
            records[request_id] = record
            validate_registry(state, records)
            _write_json(directory / "state.json", state)
            _write_json(directory / "requests" / (request_id + ".json"), record)
            _git(directory, "add", "state.json", "requests/" + request_id + ".json")
            _git(directory, "-c", "user.name=Release Number Allocator", "-c", "user.email=release-numbers@users.noreply.github.com",
                 "-c", "commit.gpgsign=false", "commit", "--quiet", "-m", "Reserve " + component + " " + str(number))
            # Normal push rejects a competing writer. No force/lease/branch deletion.
            try:
                pushed = _git(directory, "push", "--porcelain", "origin", "HEAD:refs/heads/" + branch, check=False)
            except AllocationError:
                pushed = None  # The server may have accepted a timed-out request.
            _, remote_records = _refresh(directory, branch)
            accepted = _existing(remote_records, request_id, component, source_digest, actor_id)
            if accepted is not None:
                return accepted
            if pushed is not None and pushed.returncode == 0:
                raise AllocationError("Accepted push disappeared from registry; refusing to allocate again")
        raise AllocationError("Concurrent allocation retry limit reached; retry with the same requestId")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="Write seed files only; never create Git refs")
    init.add_argument("--directory", required=True, type=pathlib.Path)
    init.add_argument("--seed", type=pathlib.Path, default=SEED)
    for name in ("validate", "lookup"):
        command = commands.add_parser(name)
        command.add_argument("--directory", required=True, type=pathlib.Path)
        if name == "lookup":
            command.add_argument("--request-id", required=True)
    command = commands.add_parser("reserve")
    command.add_argument("--remote", required=True)
    command.add_argument("--branch", default="registry")
    command.add_argument("--request-id", required=True)
    command.add_argument("--component", required=True, choices=tuple(LIMITS))
    command.add_argument("--source-digest", required=True)
    command.add_argument("--actor", required=True)
    command.add_argument("--actor-id", required=True)
    command.add_argument("--max-attempts", type=int, default=8)
    args = vars(parser.parse_args())
    operation = args.pop("command")
    try:
        if operation == "init":
            result = initialize(**args)
        elif operation == "reserve":
            result = reserve(**args)
        else:
            state, records = load_registry(args["directory"])
            result = state if operation == "validate" else lookup_request(state, records, args["request_id"])
        print(json.dumps(result, sort_keys=True))
    except (AllocationError, OSError) as error:
        print("Release number operation failed: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
