---
name: hyperboiled-server-import
description: Use when someone asks to preview or register Hyperboiled server records from static Ansible inventory, CSV, YAML, or a host list, including imports that also request Agent installation.
---

# Hyperboiled server import

Register server records in an existing, exact Hyperboiled Server Group. For a preview, show what would be registered, skipped, or left unresolved and stop before preparation or admission. A clear request to add a static inventory to an exact group authorizes registering those records. Use the Agent onboarding skill for an existing server or an interrupted installation. For registration with installation, follow both steps in order. If registration versus installation is ambiguous, ask one question in the user's language before requesting write access or making changes. Clarify any unresolved choices that would change the targets or destination.

## Resolve the source and destination

1. Inspect the selected Hyperboiled connection's live `tools/list` or native tool picker. Verify the account, organization, project binding when present, and scopes with `whoami({})`. Previews need `inventory.read`. Registration also requires granted `servers.create`, the live `servers.create` operation, and current native permission to manage the exact Server Group. Request only the scopes needed for the task in one native OAuth flow where supported. Follow the [Hyperboiled setup guide](https://hyperboiled.com/get-started.md) for user-owned browser consent. Recheck the resulting connection and resolve the targets fresh.
2. Parse only static data. For Ansible YAML/INI, flatten the requested source group to a finite set of literal hosts. Use the inventory alias as the proposed server name, `ansible_host` as the address (otherwise the alias), and `ansible_port` as the port (default 22). Accept CSV, plain YAML, and text lists when fields and mappings are unambiguous. Request a static export for a plugin, script, template, lookup, or other dynamic input. Keep passwords, tokens, Vault values, key material, SSH options, and commands out of MCP inputs, previews and reports. Importing inventory supplies no authority to execute a file, connect through SSH, or install Agent.
3. Verify a specific project with `get_project({})` for a project connection. For an organization connection, use advertised `resolve_project({"name":"…"})` for an exact project name and verify its UUID with `get_project({"project_id":"…"})`. Page through `list_project_groups` with `kind: "server-group"` and `scope: "servers.create"` to resolve a group usable for creation. On a project connection omit `parent`. On an organization connection send `parent: {"project_id":"…"}` or `parent: {}` only for an explicitly intended unassigned organization group. Pass the returned `next_cursor` as `after` until null. For a read-only preview, use `scope: "inventory.read"` if supported and mark eligibility unverified. Resolve exact group names and IDs. A missing or ambiguous destination requires clarification, not a fallback group. If the selected connection lacks the operation, return a preview and name the blocker.

## Preview the normalized plan

- For each row, keep only the name (1–120 UTF-8 bytes), literal DNS name or IP, port (integer 1–65535), deliberately chosen `environment` (`development`, `staging`, or `production`), and exact destination group. Compare endpoints locally without resolving DNS. Treat canonical IP and equivalent DNS case or trailing-dot forms as the same literal endpoint, while preserving distinct ports. Flag contradictory duplicate rows. Ask for unresolved environment, destination, or endpoint choices before admitting affected rows.
- If advertised, use `resolve_servers` with `scope: "inventory.read"`. Its `endpoint` filter takes a literal such as `web.example:22` or `[2001:db8::1]:22` and compares the stored spelling. To check for equivalent legacy spellings when it misses, page readable results without the exact endpoint filter and compare normalized endpoints locally. Follow each `next_cursor` using `after`. Verify exact endpoint, parent group UUID, environment and Inactive state. An exact existing record in the intended placement is a skip. A different placement, conflicting metadata, or multiple matches is a conflict. A complete read still covers only readable records. A limited `list_servers` can show names but cannot verify endpoints. When endpoint reconciliation is unavailable, state that limitation and wait for an authorized plan that accounts for it.
- Report the organization and exact destination, normalized candidates, already-present endpoints, conflicts and excluded counts. Protect secrets and unrelated inventory. Keep Inactive records Inactive. Import registers server records. Relinking, reconfiguration, and group creation are separate actions. For an authorized import, refresh chosen groups and verify current eligibility before preparing.

## Prepare, submit and recover

For a combined registration and installation request, check installer issuance on the same connection before the first `servers.create`. Confirm the granted `agent.enrollment.issue` scope in `whoami` and that `agent.enrollment.issue` is advertised both as a `prepare_batch.operation` and as a `get_operation_target.kind`. If issuance is unavailable, report the blocker with the preview. Proceed with registration alone only if the user chooses inventory only. Resolve the exact onboarding attempt after registration.

Prepare `servers.create` via `prepare_batch`. Each item has a stable UUID `item_id` and exactly one `create` object containing `environment`, `name`, `host`, `port`, `group_id`, and `parent_revision`. Copy the selected group's own `revision` into `parent_revision`. The group-list envelope's `parent_revision` is for creating a group. Omit the optional top-level `project_id` unless the advertised schema and task require asserting the already-bound project. It cannot select a project or switch a connection.

Example with synthetic IDs and revision:

```json
{
  "operation": "servers.create",
  "items": [{
    "item_id": "50e6c59c-1621-4537-9070-37b074b32c6c",
    "create": {
      "environment": "staging",
      "name": "staging-web",
      "host": "staging-web.example",
      "port": 22,
      "group_id": "1cc4ddf2-716e-4af1-9562-1fa2d9589417",
      "parent_revision": "opaque-selected-group-revision"
    }
  }]
}
```

- Split the authorized plan into batches of at most 20 items and 20 explicit targets, within 128 KiB decoded per request. Prepare and submit one batch at a time. Resolve the next batch's group revisions fresh. Honor `retry_after_seconds` and the server-issued expiry (10 minutes for a prepared batch).
- Retain each request ID, server-issued digest, item IDs, and expiry privately for recovery. If still preparing, call `get_batch_status({"request_id":"…"})`. When prepared, inspect the exact receipt and submit only the reviewed items using `submit_batch({"request_id":"…","digest":"…"})`. The digest represents the full prepared batch. If review changes the intended set, cancel the original preparation and prepare the approved set. Admission is atomic within a batch and rechecks current scopes, rights, revisions, and endpoint conflicts. Multiple batches can have different outcomes.
- If submit times out or the response is lost, check `get_batch_status` using the original request ID, including after updating the same connection. Replay requires the original connection version and digest. If the receipt is unavailable, reconcile exact inventory or use native recovery before retrying. For a known stale revision or denial, resolve the affected targets again. Cancel drafts with `cancel_batch` using the original request ID and digest when available.
- Summarize registered rows from native `applied` items and separate `already_exists`, unchanged or blocked rows, and unresolved receipts. If the batch is accepted but its per-item outcome is unavailable, report admission and verify the exact records through readable inventory. A hidden item stays `target_not_available`. Treat native admission as registration only.

## Install Agent and verify the first heartbeat

1. Use the exact server from its accepted `servers.create` receipt or rediscover it with read access. Confirm separately authorized SSH to the exact host and port, the expected host key, and root or sudo before requesting an installer. If the user will run it or those checks are unavailable, hand off to the exact server's current onboarding page.
2. Check the live tool catalog and `whoami` for the intended boundary and the exact scope. Use the original card.
   - For an eligible server created through MCP by the same account in the same boundary, resolve `get_operation_target` with `kind: "agent.enrollment.issue"`. This route requires `servers.create` and `agent.enrollment.issue`. Prepare an `enrollment` item with the exact `server_id`, `onboarding.id` as `attempt_id`, `enrollment.creation_request_id`, `onboarding.generation`, and `revision` as `expected_revision`.
   - For a card created in the app or by another operator, use `agent.enrollment.issue_existing` if advertised. Request that scope for the existing connection if needed. Resolve the exact server with that operation as `kind`. Prepare an `existing_enrollment` item with `server_id`, `onboarding.id` as `attempt_id`, `onboarding.generation` as `generation`, and `revision` as `expected_revision`. If the operation or a free manual attempt is unavailable, direct the user to the exact server's current onboarding page.
3. Use the server's onboarding page if the client cannot read structured tool results. Otherwise submit the fresh request ID and digest. Match each `item_id` in `structuredContent.enrollment_commands` to its receipt. Use the complete `command` exactly as returned on the verified host. It is private, single-use and valid for ten minutes. Keep it out of chat, files and logs. Confirm the first signed heartbeat, or report that Hyperboiled is still waiting for it.
4. If a submit response is lost, check `get_batch_status` with the original request ID first, including after updating the same connection. For an unavailable receipt, resolve the exact server and check the onboarding status. Report whether installation was verified, still pending, or needs recovery. Replay on the original version never returns the command. For an explicit replacement on the same-creator MCP route, fresh resolution must show an `unused` or `expired` enrollment. Use its exact ID as `reissue_enrollment_id`. For the existing-card route, recover the occupied attempt in the onboarding page.
