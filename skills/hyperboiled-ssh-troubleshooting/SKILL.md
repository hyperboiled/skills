---
name: hyperboiled-ssh-troubleshooting
description: Use when a Hyperboiled SSH grant appears present but a user cannot log in, an SSH key has not reached the server, or Web Terminal asks for verification or refuses access.
---

# Hyperboiled SSH troubleshooting

Diagnose the reported path with reads. Ask for the exact server, intended Linux user, whether the failure is in a local SSH client or Web Terminal, and the short error message when the distinction matters. Public-key fingerprints and safe error text are sufficient for matching. Keep passwords, PINs, private keys, tokens and unredacted logs out of the conversation. [Hyperboiled setup guide](https://hyperboiled.com/get-started.md)

## Verify the server and grant

1. Inspect the live tools, then use `whoami` to confirm the account, organization, project and scopes. Resolve the exact server and project placement. Check monitoring and the last heartbeat with `get_server_status`. An online Agent establishes the monitoring path. Test SSH reachability independently using only previously authorized access.
2. When available under the existing connection authority, use `list_ssh_grants` for the exact server and recipient. It requires `ssh.grant` or `ssh.revoke` and native rights. The grant-scoped read can show public-key fingerprints. The revoke-scoped read omits keys. Compare the SSH username and fingerprint to what the recipient intended to use. If that read is unavailable, ask an authorized operator to review the exact server's **SSH Access** tab and mark the unverified facts.
3. Check the original operation receipt if its request ID is available and readable. Separate the saved grant, a pending or applied Agent reconciliation, and an observed login. A grant list and an Agent heartbeat cannot prove that the intended key was applied. An `applied` result confirms reconciliation. Use a verified login or a successful SSH event that matches the intended server, account and verification time as login evidence. State explicitly if the event does not identify the key.

## Diagnose the failing path

- **Local SSH.** Match the error to the next read-only check. A timeout or refusal concerns the endpoint or route first. A host-key mismatch needs a trusted fingerprint check before connecting. An authentication denial calls for checking the selected Linux user and offered key fingerprint against the grant, then checking its recorded application. The installed key and the host's SSH policy govern local SSH. Hyperboiled MFA applies to protected app actions.
- **Web Terminal.** Check whether Web Terminal is enabled on this server, the recipient has the Terminal permission, their matching key is available in their own Vault, and fresh app verification or Vault unlock is pending. If the app reports a connection or policy block, check the server's connection mode, trusted host key and Terminal network policy with the authorized operator. Use the app for checks the MCP catalog cannot complete. The recipient completes their own verification or unlock.

Report the confirmed blocker, the evidence for it, and one next action. If several causes remain possible, say what would distinguish them. Keep grant changes, key replacement, network exceptions and SSH policy changes for an independently authorized follow-up.
