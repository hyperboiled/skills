# Hyperboiled Agent Skills

Find servers, preview or register inventory, and manage SSH access. The plugin bundles three [Agent Skills](https://agentskills.io/specification) and a Hyperboiled MCP connection.

## Install the plugin

Install for Codex or Claude Code. The plugin includes the production MCP connection. If you already configured that endpoint, [install the skills only](#install-skills-only). [Hyperboiled setup guide](https://hyperboiled.com/get-started.md)

### Codex

```sh
codex plugin marketplace add hyperboiled/skills
codex plugin add hyperboiled@hyperboiled
```

Start a new Codex session in your working project. The MCP server appears as `hyperboiled`. For the first CLI login, request inventory and session renewal explicitly.

```sh
codex mcp login hyperboiled --scopes inventory.read,offline_access
```

In the desktop app, select **Authenticate** for the bundled Hyperboiled server and review the requested access in the browser. [Codex MCP documentation](https://developers.openai.com/codex/mcp)

### Claude Code

```sh
claude plugin marketplace add hyperboiled/skills
claude plugin install hyperboiled@hyperboiled
```

Open Claude Code in your working project. In `/mcp`, select the server supplied by the Hyperboiled plugin and choose **Authenticate**, or run `claude mcp login plugin:hyperboiled:hyperboiled`. The bundled server requests inventory access and session renewal. [Claude Code marketplace](https://code.claude.com/docs/en/plugins/create-marketplace) · [Claude Code MCP](https://code.claude.com/docs/en/mcp#authenticate-with-remote-mcp-servers)

### GitHub Copilot in VS Code

Add the repository as a marketplace in **Agent Customizations**, then install Hyperboiled. Open the supplied server with **MCP: List Servers** and authenticate. Start with **Read inventory** in Hyperboiled. [VS Code agent plugins](https://code.visualstudio.com/docs/copilot/customization/agent-plugins) · [VS Code MCP](https://code.visualstudio.com/docs/copilot/customization/mcp-servers)

## Install skills only

Run this from your working project. Use your client's name in `--agent`.

```sh
npx -y skills add hyperboiled/skills --agent cursor --skill '*' --yes
```

Start a fresh session and reuse your MCP connection for the intended environment. For a new Cursor connection or another client, follow the setup guide. [Hyperboiled setup guide](https://hyperboiled.com/get-started.md)

## Verify the connection

The account holder completes browser consent on the intended Hyperboiled origin. Select the intended organization or project and start with **Read inventory**. Run `whoami` and check the account, organization, project if selected, and granted scopes before using other tools. Your current Hyperboiled permissions apply on each call.

For a task that needs writes, request only the required actions and review them in the browser. For example, registering server records requires `servers.create`.

```sh
codex mcp login hyperboiled --scopes inventory.read,offline_access,servers.create
```

For Claude Code, use the standalone skills and configure the intended connection with an explicit scope string. For the same registration task on production, configure and authenticate one entry in the working project.

```sh
claude mcp add-json hyperboiled '{"type":"http","url":"https://app.hyperboiled.com/api/v1/mcp","oauth":{"scopes":"inventory.read offline_access servers.create"}}'
claude mcp login hyperboiled
```

If a Hyperboiled connection already exists under that name, review its endpoint and grant before changing it. For Cursor, choose only the actions required when Hyperboiled offers them during consent. If the required scopes are unavailable, use an explicit-scope connection in Codex or Claude Code.

## Skills

| Skill | Example request |
| --- | --- |
| [Inventory](skills/hyperboiled-inventory/SKILL.md) | “Show the servers in Project Alpha and tell me when Agent last checked in on staging.” |
| [Server import](skills/hyperboiled-server-import/SKILL.md) | “Preview the hosts in this Ansible inventory for Project Alpha → Staging.” |
| [Managed SSH access](skills/hyperboiled-ssh-access/SKILL.md) | “Review the managed SSH grants on staging-api.” |

## Validate

From the source checkout, run `python3 ci/check_pack.py` to validate the MCP configurations, manifests, and skills and generate both archives in `dist/`. Keep the version identical across the three plugin manifests.

After building, use Python 3.11 or newer to run `python3 -B ci/check_native.py --codex codex --claude claude` in a clean local environment to check the packaged components. You can run either client separately. The check reads the Codex catalog and installs the plugin into an isolated Claude configuration.
