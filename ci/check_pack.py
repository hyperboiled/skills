"""Validate and build the distributable Hyperboiled skills and plugin."""

import json
import re
import sys
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
NAME = "hyperboiled"
SKILLS = ("hyperboiled-inventory", "hyperboiled-server-import", "hyperboiled-ssh-access")
GUIDE = "https://hyperboiled.com/get-started.md"
MCP = "https://app.hyperboiled.com/api/v1/mcp"
READ_SCOPES = ["inventory.read", "offline_access"]
SCOPED_MCP_CONFIG = ".mcp.json"
CURSOR_MCP_CONFIG = ".cursor-plugin/mcp.json"
MANIFESTS = {
    ".codex-plugin/plugin.json": SCOPED_MCP_CONFIG,
    ".claude-plugin/plugin.json": SCOPED_MCP_CONFIG,
    ".cursor-plugin/plugin.json": CURSOR_MCP_CONFIG,
}
MARKETPLACES = (".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json")
LINK = re.compile(r"\]\(([^)\s]+)\)")
URL = re.compile(r"\bhttps?://[^\s)>\x60\x22]+")
SENSITIVE = re.compile(
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----|\b(?:glpat|ghp|github_pat|sk-proj)[_-][\w-]{16,}"
    r"|\beyJ[\w-]+\.eyJ[\w-]+\.[\w-]+|\bBearer\s+[A-Za-z0-9._-]{16,}"
    r"|\b(?:password|token|client_secret)\s*[:=]\s*[\x22'][^\x22'\n]{8,}",
    re.IGNORECASE,
)


def read_payload(relative):
    source = ROOT / relative
    if source.resolve() != source or not source.is_file():
        raise ValueError(f"{relative} must be a regular file in the repository")
    text = source.read_text(encoding="utf-8")
    if SENSITIVE.search(text):
        raise ValueError(f"{relative} contains credential-shaped content")
    return text


def read_skill(name):
    relative = f"skills/{name}/SKILL.md"
    text = read_payload(relative)
    if {entry.name for entry in (ROOT / relative).parent.iterdir()} != {"SKILL.md"}:
        raise ValueError(f"{name} includes unreviewed payload files")
    prefix = f"---\nname: {name}\ndescription: Use when "
    header, separator, body = text[len(prefix) :].partition("\n---\n")
    if not text.startswith(prefix) or not separator or "\n" in header or not body.strip():
        raise ValueError(f"{name} frontmatter or body is invalid")
    if set(LINK.findall(body)) != {GUIDE} or set(URL.findall(text)) != {GUIDE}:
        raise ValueError(f"{name} must link only to the canonical public guide")
    return text


def validate_plugin(files):
    production_server = {"type": "http", "url": MCP}
    scoped_server = {
        **production_server,
        "scopes": READ_SCOPES,
        "oauth": {"scopes": " ".join(READ_SCOPES)},
    }
    for path, server in ((SCOPED_MCP_CONFIG, scoped_server), (CURSOR_MCP_CONFIG, production_server)):
        if path not in files or json.loads(files[path]) != {"mcpServers": {NAME: server}}:
            raise ValueError(f"{path} must declare only the expected production Hyperboiled MCP connection")

    versions = set()
    for path, mcp_config in MANIFESTS.items():
        manifest = json.loads(files[path])
        version = manifest.get("version", "")
        if (manifest.get("name") != NAME or manifest.get("mcpServers") != f"./{mcp_config}"
                or not re.fullmatch(r"\d+\.\d+\.\d+", version)):
            raise ValueError(f"invalid plugin identity, version or MCP reference in {path}")
        if manifest.get("skills", "./skills/") != "./skills/":
            raise ValueError(f"{path} must use the shared skills directory")
        versions.add(version)
    if len(versions) != 1:
        raise ValueError("plugin versions must match across manifests")

    sources = ({"source": "local", "path": "./"}, "./")
    for path, source in zip(MARKETPLACES, sources, strict=True):
        catalog = json.loads(files[path])
        entries = catalog.get("plugins", [])
        if (catalog.get("name") != NAME or len(entries) != 1
                or entries[0].get("name") != NAME or entries[0].get("source") != source):
            raise ValueError(f"{path} must point to the Hyperboiled plugin in the same repository")


def write_archive(name, files):
    output = ROOT / "dist" / name
    output.parent.mkdir(exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_STORED) as archive:
        for path, content in sorted(files.items()):
            entry = ZipInfo(path)
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, content.encode("utf-8"))


def build_pack():
    if {entry.name for entry in (ROOT / "skills").iterdir()} != set(SKILLS):
        raise ValueError("unexpected Hyperboiled skill directories")
    skills = {f"{name}/SKILL.md": read_skill(name) for name in SKILLS}
    plugin_files = (SCOPED_MCP_CONFIG, CURSOR_MCP_CONFIG, *MANIFESTS, *MARKETPLACES, "README.md", "assets/hyperboiled.svg")
    plugin = {path: read_payload(path) for path in plugin_files}
    validate_plugin(plugin)
    plugin.update({f"skills/{path}": content for path, content in skills.items()})
    write_archive("hyperboiled-skills.zip", skills)
    write_archive("hyperboiled-plugin.zip", plugin)


if __name__ == "__main__":
    try:
        build_pack()
        print(f"Validated {len(SKILLS)} skills and built the skills and plugin archives.")
    except (OSError, ValueError) as error:
        sys.exit(str(error))
