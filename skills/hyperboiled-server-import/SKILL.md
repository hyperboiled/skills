---
name: hyperboiled-server-import
description: Use when someone asks to preview or register Hyperboiled server records from a static Ansible inventory, a CSV, a YAML file, or a literal host list.
---

# Hyperboiled server import

Register server records in an existing, exact Hyperboiled Server Group. For a preview, show what would be registered, skipped, or left unresolved and stop before preparation or admission. An explicit request to register a clear set of hosts in an exact group authorizes that import. Ask about unresolved choices that would change the set or destination.

## Resolve the source and destination

1. Inspect the selected Hyperboiled connection's live `tools/list` or native tool picker. Verify the account, organization, project binding when present, and scopes with `whoami({})`. Start with `inventory.read`. Admission also requires granted `servers.create`, the live `servers.create` operation, and current native permission to manage the exact Server Group. Use native OAuth and the [Hyperboiled setup guide](https://hyperboiled.com/get-started.md) when additional consent is needed. The user completes browser confirmation and selects the immutable boundary. Recheck the resulting connection and resolve the targets fresh.
2. Parse only static data. For Ansible YAML/INI, flatten the requested source group to a finite set of literal hosts. Use the inventory alias as the proposed server name, `ansible_host` as the address (otherwise the alias), and `ansible_port` as the port (default 22). Accept CSV, plain YAML, and text lists when fields and mappings are unambiguous. Request a static export for a plugin, script, template, lookup, or other dynamic input. Keep passwords, tokens, Vault values, key material, SSH options, and commands out of MCP inputs, previews and reports. Importing inventory supplies no authority to execute a file, connect through SSH, or install Agent.
3. Verify a specific project with `get_project({})` for a project connection. For an organization connection, use advertised `resolve_project({"name":"…"})` for an exact project name and verify its UUID with `get_project({"project_id":"…"})`. Page through `list_project_groups` with `kind: "server-group"` and `scope: "servers.create"` to resolve a group usable for creation. On a project connection omit `parent`. On an organization connection send `parent: {"project_id":"…"}` or `parent: {}` only for an explicitly intended unassigned organization group. Pass the returned `next_cursor` as `after` until null. For a read-only preview, use `scope: "inventory.read"` if supported and mark eligibility unverified. Resolve exact group names and IDs. A missing or ambiguous destination requires clarification, not a fallback group. If the selected connection lacks the operation, return a preview and name the blocker.

## Preview the normalized plan

- For each row, keep only the name (1–120 UTF-8 bytes), literal DNS name or IP, port (integer 1–65535), deliberately chosen `environment` (`development`, `staging`, or `production`), and exact destination group. Compare endpoints locally without resolving DNS. Treat canonical IP and equivalent DNS case or trailing-dot forms as the same literal endpoint, while preserving distinct ports. Flag contradictory duplicate rows. Ask for unresolved environment, destination, or endpoint choices before admitting affected rows.
- If advertised, use `resolve_servers` with `scope: "inventory.read"`. Its `endpoint` filter takes a literal such as `web.example:22` or `[2001:db8::1]:22` and compares the stored spelling. To check for equivalent legacy spellings when it misses, page readable results without the exact endpoint filter and compare normalized endpoints locally. Follow each `next_cursor` using `after`. Verify exact endpoint, parent group UUID, environment and Inactive state. An exact existing record in the intended placement is a skip. A different placement, conflicting metadata, or multiple matches is a conflict. A complete read still covers only readable records. A limited `list_servers` can show names but cannot verify endpoints. When endpoint reconciliation is unavailable, state that limitation and wait for an authorized plan that accounts for it.
- Report the organization and exact destination, normalized candidates, already-present endpoints, conflicts and excluded counts. Protect secrets and unrelated inventory. Keep Inactive records Inactive. Import registers server records. Relinking, reconfiguration, and group creation are separate actions. For an authorized import, refresh chosen groups and verify current eligibility before preparing.

## Prepare, submit and recover

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
- If submit times out or the response is lost, check the original `get_batch_status` on the same connection. When replay is still warranted, use the original request ID and digest. Never create a new batch to resolve an unknown outcome. If the connection changed or expired and the original receipt is unavailable, report that state and reconcile exact inventory or use the native browser recovery path before considering any new reviewed batch. A known stale revision or denial calls for fresh resolution and current authority. To cancel before admission, use the original `cancel_batch` request ID and digest (empty only if none was issued).
- Summarize registered rows from native `applied` items and separate `already_exists`, unchanged or blocked rows, and unresolved receipts. If the batch is accepted but its per-item outcome is unavailable, report admission and verify the exact records through readable inventory. A hidden item stays `target_not_available`. Treat native admission as registration only. Leave Agent enrollment, SSH, access grants, and host changes to separate requests.
