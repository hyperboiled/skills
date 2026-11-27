---
name: hyperboiled-ssh-access
description: Use when someone asks to review Hyperboiled managed SSH grants, grant selected public keys to a Linux account on a server, revoke an exact grant, or check Agent reconciliation for one of those changes.
---

# Hyperboiled managed SSH access

Work through the selected Hyperboiled MCP connection. A review or preview ends after read-only discovery. An explicit request with exact, verified choices authorizes the named grant or revoke. Ask only about unresolved choices that would change the action.

## Establish authority and resolve the server

1. Inspect the native MCP tool catalog and use the advertised schemas. Call `whoami({})` to verify the current account, organization, bound project when present, and scopes. For a project connection confirm `get_project({})`. For an organization connection and a named project, resolve its exact visible UUID and match the server's parent group UUID to that project's groups where needed. Follow `next_cursor` with `after` on paginated reads.
2. Start with `inventory.read`. Grant and revoke each need their corresponding granted scope and current native authority on the exact server, including network access policy. OAuth consent applies to the selected boundary, and `offline_access` adds no business rights. For a missing scope or mismatched connection, use the account holder's native OAuth flow and repeat discovery on the authorized connection. Keep credentials and callback URLs private. [Hyperboiled setup guide](https://hyperboiled.com/get-started.md)
3. Use `resolve_servers` with the live schema and the relevant `scope: "ssh.grant"` or `"ssh.revoke"` for action-specific results. Use `ids` for known UUIDs or `q` to find candidates. Verify the UUID, endpoint, placement and environment as relevant. Check name matches for ambiguity. Hidden or denied results are unresolved, including when the same name is visible in another project. Proceed only on the intended boundary. Missing tools or native authority stop the action. Keep shell, SSH, Terminal, Vault and direct API access outside this workflow.

## Review and choose the exact change

- **Review:** Call `list_ssh_grants({"server_id":"…","scope":"ssh.grant"})` or the granted `"ssh.revoke"` scope. Optionally include exact `member_id`. The grant-scoped read can include key IDs, names and fingerprints. The revoke-scoped read omits keys. Report only the relevant placement, Linux user, groups, desired state and any separately confirmed Agent evidence. Inventory-only rights cannot verify existing grants.
- **Grant:** Find an eligible recipient with `find_project_members({"server_id":"…","purpose":"ssh.grant","q":"…"})` and verify the exact member UUID. Use `get_grant_options({"server_id":"…","member_id":"…"})` to resolve active key IDs, fingerprints, allowed Linux group inputs, a username suggestion and the revision. Select the user-authorized key IDs and Linux username. A suggested username or bootstrap account is not a selection. Supply the explicitly selected, valid, unique supplementary groups, using `[]` when the intent is no supplementary groups. Never infer `sudo`, root, privileged groups or a default key set. Keep raw keys and secrets out of the operation and report. Agent can create a missing supported Linux account during reconciliation. An active grant for the same server, member and Linux user is an existing placement, not an update target for `ssh.grant`. Report an exact match or clarify a conflict.
- **Revoke:** Resolve with `list_ssh_grants({"server_id":"…","scope":"ssh.revoke","member_id":"…"})` when the member UUID is known. Choose the exact active grant UUID on the selected server. Check the recipient and Linux user, especially when the same member has several grants. Revocation concerns that managed placement. The Linux account and already-open SSH sessions remain, and other access may still exist.

## Submit and follow the native receipt

Use `prepare_batch` with `{"operation":"…","items":[…]}`. Each item carries a stable UUID `item_id` and exactly one payload from the table. Re-resolve stale bindings and preserve the exact authorized choices.

| Operation | Item payload |
| --- | --- |
| `ssh.grant` | `grant: {server_id, member_id, target_linux_user, public_key_ids, linux_groups, expected_revision}`. Use 1–64 unique key IDs and copy `get_grant_options.revision`. |
| `ssh.revoke` | `revoke: {server_id, grant_id, expected_grant_revision}`. Copy the exact grant row's opaque `revision` from `list_ssh_grants`. |

- Use at most 20 items and 20 explicit targets within 128 KiB decoded per batch. Inspect the exact prepared receipt. Poll `get_batch_status({"request_id":"…"})` if preparing. Submit before expiry using only `submit_batch({"request_id":"…","digest":"…"})` with the server-issued digest. One changed or unauthorized target blocks the whole admission. Honor `retry_after_seconds` and native busy states.
- Retain the request ID and digest privately. On a lost response, inspect the original receipt on the same connection. If a replay is needed, reuse the same request ID and digest. Never issue a fresh batch to resolve an unknown submission. Cancel only before admission via `cancel_batch` with that request ID and digest (empty only if none was issued). After admission, use the exact receipt and its `child_request_id` and `native_id` when readable to identify the original operation for native recovery. If the client offers no supported recovery action, report the unresolved state and hand off that exact operation to the authorized operator. A new connection or scope version cannot adopt the original preparation.
- Batch `accepted` means desired policy was admitted. Read each item's own state. `accepted` or `applying` may still be queued or awaiting Agent reconciliation. `applied` is the recorded native Agent result, without proof of an actual end-user login or termination of an existing session. `observed_at` alone can reflect an intermediate observation. Report offline or unavailable confirmation as pending or unknown according to the receipt. For `failed`, `conflict`, `unknown`, or `target_not_available`, report the exact state and follow supported native recovery for the original operation. An accepted revoke is reversed only through a new authorized grant, after resolving the original outcome.
