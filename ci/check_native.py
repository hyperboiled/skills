"""Optional local check of the extracted ZIP with native clients, without MCP login."""

import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from check_pack import MCP, NAME, ROOT, SKILLS


def executable(value):
    path = shutil.which(value)
    if path is None:
        raise argparse.ArgumentTypeError(f"executable not found: {value}")
    return str(Path(path).resolve())


async def codex_catalog(binary, plugin, state):
    home = state / "codex"
    home.mkdir()
    server = await asyncio.create_subprocess_exec(
        binary, "app-server", "--listen", "stdio://",
        "-c", "analytics.enabled=false", "-c", "features.apps=false",
        "-c", "sqlite_home=" + json.dumps(str(state)),
        "-c", "log_dir=" + json.dumps(str(state)),
        cwd=state, env=dict(os.environ, CODEX_HOME=str(home)),
        stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
    )

    async def request(message):
        server.stdin.write(json.dumps({"jsonrpc": "2.0", **message}).encode() + b"\n")
        await server.stdin.drain()
        if "id" not in message:
            return None
        while line := await server.stdout.readline():
            reply = json.loads(line)
            if reply.get("id") == message["id"]:
                if "error" in reply:
                    raise ValueError(f"{message['method']}: {reply['error']['message']}")
                return reply["result"]
        raise ValueError(f"Codex exited before replying to {message['method']}")

    try:
        async with asyncio.timeout(20):
            await request({"id": 1, "method": "initialize", "params": {
                "clientInfo": {"name": "hyperboiled-package-check", "version": "1"},
            }})
            await request({"method": "initialized"})
            result = await request({"id": 2, "method": "plugin/read", "params": {
                "marketplacePath": str(plugin / ".agents/plugins/marketplace.json"),
                "pluginName": NAME,
            }})
    except TimeoutError as error:
        raise ValueError("timed out reading the Codex plugin catalog") from error
    finally:
        if server.returncode is None:
            server.kill()
        await server.wait()

    details = result["plugin"]
    names = sorted(skill["name"].removeprefix(f"{NAME}:") for skill in details["skills"])
    if names != sorted(SKILLS) or details["mcpServers"] != [NAME] or details["hooks"]:
        raise ValueError(
            f"unexpected Codex components: skills={names}, "
            f"MCP servers={details['mcpServers']}, hooks={len(details['hooks'])}"
        )
    print(f"Codex discovered all {len(SKILLS)} skills and one MCP server.")


def claude_catalog(binary, plugin, state):
    env = dict(os.environ, CLAUDE_CONFIG_DIR=str(state / "config"),
               DISABLE_AUTOUPDATER="1", DISABLE_TELEMETRY="1", NO_COLOR="1")

    def run(directory, *command):
        result = subprocess.run([binary, *command], cwd=directory, env=env,
                                capture_output=True, text=True, timeout=20)
        if result.returncode != 0:
            raise ValueError((result.stderr or result.stdout).strip())
        return result.stdout

    validated = run(plugin, "plugin", "validate", "./")
    if f"mcpServers: {NAME} http {MCP}" not in validated:
        raise ValueError("Claude did not validate the production MCP server")
    run(plugin, "plugin", "marketplace", "add", "./")
    run(plugin, "plugin", "install", f"{NAME}@{NAME}")
    details = run(state, "plugin", "details", f"{NAME}@{NAME}")
    if f"Skills ({len(SKILLS)})" not in details or any(name not in details for name in SKILLS):
        raise ValueError("Claude did not discover the expected Hyperboiled skills")
    if f"MCP servers (1)  {NAME}" not in details or "Hooks (0)" not in details:
        raise ValueError("unexpected Claude plugin server or hook count")
    print(f"Claude installed the plugin and discovered all {len(SKILLS)} skills and one MCP server.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex", type=executable, help="Codex CLI executable")
    parser.add_argument("--claude", type=executable, help="Claude Code executable")
    args = parser.parse_args()
    if not (args.codex or args.claude):
        parser.error("choose at least one native client to check")

    with TemporaryDirectory(prefix="hyperboiled-native-") as directory:
        state = Path(directory).resolve()
        plugin = state / "plugin"
        with ZipFile(ROOT / "dist/hyperboiled-plugin.zip") as archive:
            archive.extractall(plugin)
        if args.codex:
            asyncio.run(codex_catalog(args.codex, plugin, state))
        if args.claude:
            claude_catalog(args.claude, plugin, state)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        sys.exit(str(error))
