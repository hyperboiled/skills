---
name: hyperboiled-member-offboarding
description: Use when someone asks to offboard a Hyperboiled member, preview the effect of disabling their organization membership, or verify their application access and managed SSH removal.
---

# Hyperboiled member offboarding

Identify the exact person, organization and intended reach of the change. Disabling an organization membership, removing a resource assignment, and revoking an individual SSH grant have distinct effects. Use the managed SSH access skill for an individual grant. Clarify phrases such as “remove this person” when the target or reach is ambiguous. A preview request stays read-only. [Hyperboiled setup guide](https://hyperboiled.com/get-started.md)

## Preview current impact

1. Verify `whoami`, the live MCP catalog and the selected boundary. Organization disable requires an organization connection with `members.manage` and current native authority. For a new disable, resolve the active linked human membership using `list_organization_members`. For an already-disabled member, read its recorded outcome. Continue the original cleanup only when requested. Respect the role hierarchy, last Owner safeguard and current native blockers. Use the normal account flow for leaving your own organization.
2. For organization disable, read `get_organization_member_lifecycle_impact` with `action: "disable"` for that member. Use its full placement count and at most 20 detailed managed placements. Review relevant direct and inherited resource roles separately through available authorized roster views. Highlight scopes you could not inspect and any offline or unverified Agent on which physical key removal may lag.
3. For project, group or server removal, resolve the exact direct source and current version with the resource roster. Use `get_resource_member_removal_impact` to review inherited authority, eligible and blocked descendants, and managed SSH impact for each choice. A surviving inherited role requires review at its source. Resolve the intended descendant removal and managed SSH consequences before submission.

## Apply the authorized change and follow cleanup

For explicitly requested organization disable, use `members.disable` with the exact `member_disable` item, current `expected_access_revision` and `impact_sha256` from the preview. For scoped removal, use `resource_members.remove` with the exact direct version, `preview_token` and explicit `remove_direct_descendants` and `confirm_ssh_revocation` choices. Refresh the preview if the impact changes. Use the native browser flow when the action or required evidence is unavailable through the selected connection.

Prepare and submit the exact authorized operation using the server-issued request ID and digest. When a reply is lost, read the original receipt and native progress before scheduling any retry.

- **Organization disable.** The MCP lifecycle receipt reports membership status and the number of SSH operations. Open **Members → the exact member → Lifecycle progress** for the original operation and its per-server removal results.
- **Scoped removal.** Reread effective access and retained assignments. `resource_removal_ssh`, when present, gives counts. The server's **SSH Access** tab can show pending and failed revokes. Completed revokes can drop out of the attention list. **Revoked history** records app state.

Report app access and physical key removal separately. Confirm removal only with the matching native Agent result for that server and managed placement. Use **pending** for recorded work awaiting confirmation and **unverified** when the result is unavailable. Include incomplete coverage for hidden or truncated results. A disabled membership, operation count or aggregate cannot identify which server confirmed removal. An offline server may still accept new direct SSH with the old key until Agent confirms removal. Already-open direct SSH sessions and unmanaged copies need separately authorized investigation. Reactivation restores membership eligibility. Review any required role or grant restoration separately.
