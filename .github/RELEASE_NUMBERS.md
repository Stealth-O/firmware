# Release number allocation

This infrastructure only reserves numbers. Firmware is built locally from a
developer's source checkout. No private firmware source, signing key, binary or
build log is sent to this workflow.

`firmware` and `bootloader` are independent global counters. One firmware number
can identify a release across multiple device targets; request it once for that
release, not once per image. The planned fields use 20 bits for firmware
(1,048,576 values: zero unknown, 1…1,048,575 usable) and 12 bits for bootloader
(4,096 values: zero unknown, 1…4,095 usable), totaling four bytes. Exhaustion is
an error, never a wraparound.

## Owner setup

1. Publish this `.github` directory to the repository's default `main` branch.
   Enable Actions and allow the workflow's `contents: write` permission.
2. Review the initial seed against existing release history. It withholds
   firmware 1…8 and bootloader 1…5; the first new numbers are 9 and 6. These
   reservations do not map legacy semantic versions to numeric IDs.
3. Create `registry` once as a separate root history. From this repository root:

   ```bash
   allocator_script="$PWD/.github/scripts/release_numbers.py"
   registry_checkout="$(mktemp -d "${TMPDIR:-/tmp}/stealtho-registry.XXXXXX")"
   python3 "$allocator_script" init --directory "$registry_checkout"
   git -C "$registry_checkout" init --initial-branch=registry
   git -C "$registry_checkout" add state.json
   git -C "$registry_checkout" commit -m "Initialize release number registry"
   git -C "$registry_checkout" remote add origin git@github.com:Stealth-O/firmware.git
   git -C "$registry_checkout" push origin registry:refs/heads/registry
   ```

   An existing registry must be reused. Do not force this push, reset counters,
   delete the branch, or initialize a replacement after a failure. A normal
   push of this independent root cannot replace an existing registry history.
   The allocator itself never creates a missing branch.
   These bootstrap commands use the owner's Git SSH access to the repository;
   authenticating `gh` for the later HTTPS API client does not configure SSH.
4. Protect `registry` against force pushes and deletion while allowing normal
   fast-forward writes by this workflow's token. Required-PR rules or an
   organization policy may prohibit this token from pushing; resolve that
   policy explicitly before use. `contents: write` does not bypass protection.

Only `state.json` and `requests/<UUID>.json` belong on `registry`; keep this
guide and allocator code on `main`. Do not add firmware artifacts to `registry`.

## Request contract

Dispatch `allocate-release.yml` at `main` with:

- `component`: `firmware` or `bootloader`;
- `request_id`: a fresh canonical UUID4, saved before dispatch;
- `source_digest`: 64 lowercase hexadecimal characters identifying the prepared
  source snapshot (not a claim that a binary already exists).

The local development client prepares and retains these values. Repeat the
same UUID, component and digest after a timeout; never request another number
just to recover a lost response. GitHub supplies the original actor and stable
actor ID. The same actor ID must own a retried request, even after a login rename.

Read the result from `requests/<UUID>.json` on `registry`, including after a
workflow timeout. It contains the allocated number, component, source digest,
request ID, actor, actor ID and UTC creation time. This metadata is public in a
public repository. There is no later package-ready update; canceled builds
keep their reservations. Build and image records remain in development branches.

The workflow runs trusted code from its immutable `main` commit. Concurrent
requests race through normal Git fast-forward push; a rejected or ambiguous
push is reconciled by UUID before another allocation attempt. Counter and
request are one commit. Separate clients and worktrees need no shared file lock.
The complete linear registry history is checked before allocation: after the
seed, each commit must add one request and increment its counter. Reverts,
edited records, merges and squashed history are rejected. Do not rewrite or
tidy this history.

The guarantee assumes trusted writers and retained Git history. Repository
administrators and other workflows with write permission can still alter data.
Protect and retain this branch; Actions logs/artifacts are not the registry.

References: [manual dispatch](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow),
[workflow token permissions](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token),
[protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).
