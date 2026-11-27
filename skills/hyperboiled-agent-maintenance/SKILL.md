---
name: hyperboiled-agent-maintenance
description: Use when someone asks to update Hyperboiled Agent on one or many servers, plan a fleet rollout, verify a running Agent release, or resume an Agent update with an uncertain outcome.
---

# Hyperboiled Agent maintenance

Confirm the intended organization, project, server set and release intent. Verify the selected connection with `whoami` and inspect the live catalog for `agent.update` and its resolver. Work through the native signed release workflow. [Hyperboiled setup guide](https://hyperboiled.com/get-started.md)

## Resolve the rollout

- Resolve each named server and current Agent. Use `get_operation_target` with `kind: "agent.update"` on each host. With no release ID, it resolves the compatible current catalogue release. Use a specific content-addressed release ID only when requested.
- Use each host's observed `agent_id`, `architecture`, `expected_release_id`, selected `release_id` and current revision. Release IDs are exact 64-character lowercase hex values. Record the current runtime and target per host. Treat already-current hosts, unavailable releases, incompatible architecture and busy or recovery states separately. A release resolved for one architecture or Agent cannot be assumed to apply to another.
- Show the selected hosts, the pinned releases and any blockers. For a fleet rollout, work in bounded cohorts of at most 20 targets. Use a small first cohort when the requested rollout permits it. Recheck readiness before continuing with later cohorts if verification is incomplete or a host failed.

## Submit and verify the running runtime

Prepare `agent.update` using each host's exact `update` item and revision. Submit the server-issued request ID and digest. Admission is atomic for that batch. Each host subsequently produces its own result. Keep the original request and item references for status and recovery.

Use `get_batch_status` for the original request and the native update operation for each target. A receipt's requested `agent_update.release_id` records intent. Credit a verified update only when the matching native operation reports `observed` for that target release or a fresh authoritative Agent runtime observation confirms the exact release on that Agent. A reboot, accepted task, progress phase or heartbeat without release evidence leaves the update unverified.

Report verified, already current, in progress, failed, rolled back or unresolved results per host. Keep the original request for a lost reply or an unknown outcome. Inspect its native operation and follow supported recovery before any new admission for that host. Use the native failure and rollback evidence when reporting what is running now.
