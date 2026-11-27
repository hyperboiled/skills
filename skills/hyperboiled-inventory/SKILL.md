---
name: hyperboiled-inventory
description: Use when someone asks to list or find Hyperboiled servers or projects, check a server's monitoring status, or diagnose an empty inventory, authorization error, or unexpected Hyperboiled MCP connection.
---

# Hyperboiled inventory

Use the configured Hyperboiled MCP connection for read-only inventory. A result describes what the current account can see in its approved boundary at the time of the read.

## Establish the boundary

1. Inspect the selected server's live MCP tool catalog through the client’s `tools/list` or tool picker. Use only advertised tools and input schemas. If the connection is missing or sign-in is needed, use the assistant's native OAuth flow and the [Hyperboiled setup guide](https://hyperboiled.com/get-started.md). The account holder completes sign-in and consent. Keep tokens and sign-in or callback URLs out of the chat, files, and reports.
2. Call `whoami({})` to check the account, organization, bound project when present, and granted scopes. Inventory requires `inventory.read`. `offline_access` enables refresh and confers no inventory or write rights. For a project connection, confirm with `get_project({})`. For an organization connection, use `list_projects` or `resolve_project` when advertised and `get_project({"project_id":"…"})` for an exact visible UUID.
3. If the requested organization or immutable project binding differs, report the mismatch. Use a different connection only when it has been authorized for the intended boundary and the user selected it for this task. Repeat the checks on that connection. A requested scope or browser login is not proof of granted scope or current native access.

## Read and report

| Need | MCP tool and inputs |
| --- | --- |
| List readable servers | `list_servers` takes optional `limit` (1–100, default 25) and `after`. Follow `next_cursor` until null using the same connection and query. This tool has no project or name filter. |
| Find an exact server | Use `resolve_servers` when advertised, with `scope: "inventory.read"` and the supported `ids`, `q`, or `endpoint` arguments. Treat name matches as candidates. For a requested project on an organization connection, match a returned parent group UUID to the exact parent's groups using advertised `list_project_groups` with `kind: "server-group"`, `scope: "inventory.read"`, and `parent: {"project_id":"…"}`. Follow group pages with `after` from `next_cursor` until the group is matched or the cursor is null. If the live reads cannot establish that relationship, report it as unresolved. |
| Check monitoring | Call `get_server_status({"id":"…"})` for the exact readable UUID. Report the returned status and last accepted heartbeat, if present. A heartbeat is an observation, and a missing heartbeat supplies no proof of reachability or host existence. |

If the current tool list lacks a necessary read, use a supported narrower read or report the gap. A 401 calls for native reauthentication on the intended connection. A 403 calls for checking the granted scope and current native access. Missing, hidden, ambiguous, partial, and failed results have different meanings. Avoid inferring absence outside the current readable boundary or using SSH, browser sessions, tokens, or direct API calls to bypass visibility.

Return only the fields needed to answer the request. For an audit, include the matched boundary, exact lookup criteria, native status or visible match, observation time, and whether all pages were read. For example, say “No readable match in Project Alpha after all pages were checked” only after confirming that exact project and completing the read. Keep raw tool dumps, unrelated hosts and opaque values out of the report.
