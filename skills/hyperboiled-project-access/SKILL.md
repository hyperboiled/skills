---
name: hyperboiled-project-access
description: Use when someone asks who can access a Hyperboiled Project, Server Group or Server, whether roles are inherited, how to give a team different access to dev and prod, or how to move a server between Server Groups.
---

# Hyperboiled project access

Identify the organization, exact project and groups or servers. When “access” is ambiguous, ask whether the user means inventory visibility, an app action such as Terminal or Operations, or SSH login as a named Linux user. Report each requested layer separately. [Hyperboiled setup guide](https://hyperboiled.com/get-started.md)

## Inspect current access

1. Check the advertised catalog and `whoami`. Resolve the exact project. Use `list_project_groups` with `kind: "server-group"` and the intended project parent when the connection is organization-wide. Use `get_group_links` for the relevant groups and follow all applicable pages. Shared servers can have several paths. Use exact resource IDs and retain the connection's visibility boundary in the report.
2. When available, use `list_resource_members` for `project`, `server-group` and `server`. This read uses the `resource_members.manage` scope and current rights. Use the reported `effective_role`, `inherited_role` and `sources`. Follow `next` with `after`. The highest direct or inherited resource role applies. Active organization Owners and Managers inherit management authority. A row with no effective role at the project can have a role on a descendant. Verify the capability needed for the task on the actual target.
3. A project-bound roster can omit people whose only access to a shared server comes through another project, even after pagination is complete. Mark exclusivity unverified where relevant paths or sources are hidden or truncated. For physical SSH, separately check authorized managed grants for the exact hosts, users and keys, and follow `next_cursor` with `after` when checking who has grants. Scope the result to visible managed placements and any independent authorized host evidence. If the needed read is unavailable, hand off to the exact resource's Members or SSH Access view.

## Propose or make the requested change

For “the team uses dev and only two people use prod”, compare each environment's effective access with the named policy. Prefer assigning the team at the dev Server Group and the approved people at the prod Server Group when the intent is isolation. Identify project-level roles, organization administrators, direct host assignments, shared paths and old SSH grants that could still give prod access. Adding two people to the prod group does not remove a broader inherited role. Name any exceptions and unresolved facts before saying prod is restricted.

A review or proposed layout ends with a short matrix of people, resources, intended role, observed role/source and managed SSH status. Apply only an explicitly requested, unambiguous change. For role writes, use the current direct assignment version, or zero for a verified new direct assignment. Use the native removal impact preview before removing a role and resolve the desired descendant and SSH consequences. Submit through the normal typed batch workflow, then reread the exact effective roles and any separately changed grants. Keep physical SSH revocation or grant creation tied to the user's explicit selection.

For a server move, copy the exact server's `revision` from `resolve_servers` into `group_edge.related_revision` on `server_groups.servers.link` and `server_groups.servers.unlink`. Use `group.revision` and `links_revision` from `get_group_links` for the exact group, and set `expected_present` from the observed link. When a temporary shared link is acceptable, verify the destination link and refresh revisions before unlinking the source. On a project-bound connection, removing the last link first can make the server unavailable.
