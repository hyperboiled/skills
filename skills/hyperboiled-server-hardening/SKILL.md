---
name: hyperboiled-server-hardening
description: Use when someone asks to enable key-only SSH or Fail2Ban in Hyperboiled, verify a staged SSH policy, or recover a hardening operation that has not finished.
---

# Hyperboiled server hardening

Confirm the requested servers, whether the user wants key-only SSH, Fail2Ban, or both, and the intended trusted networks. Inspect the live tool catalog and verify the account, organization, project and scopes with `whoami`. Resolve exact servers and current Agent identities. Use the native operations advertised for that deployment. [Hyperboiled setup guide](https://hyperboiled.com/get-started.md)

## Enable key-only SSH

1. Resolve `operations.ssh_key_only.responsible_access` under `operations.ssh_key_only` to find an eligible deployed grant. Confirm the exact member, grant, public key and Linux username. Use the resolver's sole eligible selection when it matches the request. Clarify different or ambiguous selections. A requested grant still awaiting deployment needs reconciliation first. Preserve a current valid selection and use its native phase to continue.
2. Prepare the responsible-access selection only when the native flow requires it. Use the returned bindings, current revision and explicitly intended additional `user_trusted_cidrs`. Use an empty list for no additional exemptions. For `needs_ssh_verification` follow the returned onboarding link on the selected origin. Before staging, obtain a fresh successful external SSH login for the selected Linux user and key. Use the existing authorized SSH path or ask its operator to perform the check.
3. Wait for native Agent observation, resolve `operations.ssh_key_only` again and copy the matching `key_only.proof_id` into the stage item. Stage only hosts with current proof and retain independent operator access. Read each host's `awaiting_proof` receipt, `rollback_deadline` and same-origin verification link after staging. The host has its own 15-minute rollback window. Verify a new matching external SSH login within that window. Web Terminal, TCP reachability and a pre-stage login cannot establish post-stage proof.
4. Report verified policy, proof still needed, failure or observed rollback per host. A retry leaves the original deadline in effect. For missing proof or an unknown outcome, read the original operation and follow native recovery. Use the native `observed`, `rolled_back` or `recovery_required` outcome when available.

## Apply and verify Fail2Ban

Use the separate `operations.fail2ban` scope. Resolve `operations.fail2ban.standalone` for a standalone action or `operations.fail2ban.onboarding` for the current onboarding attempt. Follow native preflight blockers. If both actions were requested in onboarding, finish key-only proof first. Use `trusted_policy.kind` of `explicit_cidrs` with the exact approved list, or `saved_policy` with the returned ID, revision and digest. The onboarding list must match the current responsible-access selection. Hyperboiled supplies its environment-owned gateway allowances. A requested reprovision needs its reviewed preflight ID.

For a Fail2Ban-only request in manual onboarding, resolve `needs_responsible_access` using the eligible deployed grant and matching Linux user and key. If authorized, record the selection through `operations.ssh_key_only.responsible_access`. For `responsible_access_stale`, follow the same-origin onboarding link to repair the existing selection. For `needs_ssh_verification`, use the same-origin link for the matching external SSH login and wait for Agent proof. Use the current onboarding page if selection is unavailable through MCP. Once the proof is observed, resolve the Fail2Ban target again. SSH policy staging requires a request for key-only SSH.

Prepare the exact eligible set with current bindings, stable item IDs and the approved policy. Keep the original input to verify the policy and targets. If the receipt is `preparing`, poll `get_batch_status` for the original `request_id` with a bounded wait and respect retry hints. Stop if any item becomes `target_not_available`. Report a blocker, expiry, loss of visibility, or still-pending request when the wait ends. Submit only when the original request is `prepared`, has a server-issued digest, and every item ID and target matches the original input. If submission loses its reply, read the original receipt before retrying.

Track the result per server. Verify that the intended jail is active on the detected SSH port, using native observation or an authorized operator check. If enforcement is unavailable to observe, report that separately from configuration acceptance.
