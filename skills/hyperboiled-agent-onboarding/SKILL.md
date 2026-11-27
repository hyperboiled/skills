---
name: hyperboiled-agent-onboarding
description: Use when someone asks to install Agent on existing Hyperboiled server cards, resume an interrupted installation, replace an expired installer, or verify the first heartbeat after onboarding.
---

# Hyperboiled Agent onboarding

Use the selected connection's advertised tools and verify the account, organization, project binding and scopes with `whoami`. Resolve every named server to an exact readable card and check its host, SSH port and existing Agent state. Clarify ambiguous targets. For static inventory registration, use the server import skill. For a progress check, read the existing state. [Hyperboiled setup guide](https://hyperboiled.com/get-started.md)

## Continue the original attempt

1. If a previous submission lost its reply, read `get_batch_status` with the original request ID first. Use the same account, membership and boundary after reauthorization. Replay requires the original connection version and digest and returns a receipt without the installer. If the receipt is missing or hidden, reconcile the exact card and its native onboarding. Keep a timeout or missing heartbeat pending or unverified until the current attempt can be identified and the available action is clear.
2. For an explicitly requested issuance on an eligible attempt, use `get_operation_target` with the matching advertised kind and its current bindings.
   - For an eligible card created through MCP by the same account, use `agent.enrollment.issue` with `servers.create`. The `enrollment` batch item uses the server ID, current attempt ID and generation, the original creation request reference and current revision. A separately requested replacement requires an `unused` or `expired` enrollment and its exact `reissue_enrollment_id`.
   - For an existing app-created card or a card created by another operator, use `agent.enrollment.issue_existing` when advertised. The `existing_enrollment` item uses the server ID, current attempt ID and generation and current revision. A missing, occupied, failed or expired manual attempt goes through native onboarding recovery. Preserve the original server card.
3. Use the server card when the applicable operation or client structured output is unavailable, native recovery is required, or the operator will run the command. Some versions require the creation and installer issuance to use the same OAuth connection version. If the resolver cannot establish eligibility for the exact card after reauthorization, continue in the server card. Preserve the card and continue its current attempt when available.

## Continue in the server card

Open **Servers → the exact server → Settings → Resume onboarding**. Use a returned link only on the selected Hyperboiled origin and for that server. Check the current attempt before using its installation action. For a first issuance, use **Get installation command**. If a command was already issued and is still valid, **Generate new installation command** invalidates it. Use that action only if the user explicitly requested replacement. If Agent has already registered, track the first heartbeat for that attempt. For an expired or failed attempt, follow the recovery shown on the card. If the required action is unavailable under the current rights, report the blocker and hand off that card to an authorized operator.

On a revoked card, **Resume onboarding** opens recovery and submitting it starts a fresh attempt. For a status-only request, report the state and the recovery path. Submit recovery only when the user requested it. Report each server separately and continue reading the other authorized targets.

## Install and verify

For an explicitly requested installation over separately authorized SSH, verify the exact host key, port and root or sudo access before requesting the command. Keep each prepared request ID, digest and item ID together. Review the exact preparation and submit with the server-issued request ID and digest. Match each `structuredContent.enrollment_commands` entry to its item and execute its complete command only on the verified host. It is private, single-use and valid for ten minutes. Avoid displaying or saving the command or any enrollment material. Web Terminal is optional.

Read the current `enrollment.state` for each item in the original receipt when available. An outer `applied` can mean that issuance alone succeeded. Use native onboarding or the current enrollment's `installed` state as first heartbeat evidence. The monitoring state and timestamp from `get_server_status` describe the card. Correlate them to this attempt when an earlier Agent or heartbeat exists. Report one state per server.

- **Connected** when the current installation is confirmed by a heartbeat.
- **Awaiting heartbeat** after `consumed` or when execution of the current installer is confirmed and heartbeat confirmation is pending.
- **Action needed** for an `unused` installer that still needs to run, an `expired` or `superseded` installer, an occupied attempt requiring recovery, a lost installer, an explicit failure or an unavailable install path. Name the specific next step and only use the current eligible attempt.
- **Unverified** when the available data cannot distinguish those states.

Use bounded status checks while progress is expected and respect retry hints. At the end of the check, provide the last observation and where to resume for each unfinished server. A lost reply, an installer exit and an old heartbeat are separate observations.
