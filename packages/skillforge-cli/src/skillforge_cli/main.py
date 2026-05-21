"""SkillForge CLI — scaffold, validate, install, publish, search, and list skills."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Optional

import click
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.syntax import Syntax

from skillforge_core.parser import parse_skill_md, validate_skill

from . import __version__
from .config import get_skills_dir, load_config, set_config_value
from .registry import RegistryClient

console = Console()


# ═══════════════════════════════════════════════════════════════════════════════
# Helper utilities
# ═══════════════════════════════════════════════════════════════════════════════

SKILL_MD_TEMPLATE = """---
name: {name}
version: 0.1.0
description: A short description of what this skill does (10-500 chars)
author: Your Name
license: MIT
tags:
  - example
---

# {title}

## Overview

A brief introduction to your skill.

## Tools

| Tool | Description | Risk |
|------|-------------|------|
| example-tool | Does something useful | low |

## Installation

```bash
skillforge install {name}
```

## License

MIT
"""


def _get_registry_client(ctx: click.Context) -> RegistryClient:
    """Get or create a RegistryClient from CLI context."""
    return RegistryClient(base_url=ctx.obj.get("registry_url"))


def _show_validation_results(filepath: Path, errors: list[str], body: str) -> None:
    """Pretty-print skill validation results."""
    if not errors:
        console.print(
            Panel.fit(
                f"[bold green]✓[/bold green] {filepath} is a valid SKILL.md\n\n"
                f"[dim]Body: {len(body)} chars[/dim]",
                title="Validation Passed",
                border_style="green",
            )
        )
    else:
        console.print(
            Panel.fit(
                f"[bold red]✗[/bold red] {filepath} has {len(errors)} validation error(s)",
                title="Validation Failed",
                border_style="red",
            )
        )
        for i, error in enumerate(errors, 1):
            console.print(f"  [red]{i}.[/red] {error}")


def _read_skill_file(path: Path) -> str:
    """Read a SKILL.md file, with friendly error on failure."""
    if not path.exists():
        raise click.ClickException(f"File not found: {path}")
    return path.read_text(encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════════
# Main CLI group
# ═══════════════════════════════════════════════════════════════════════════════

@click.group()
@click.version_option(version=__version__, prog_name="skillforge")
@click.option(
    "--registry-url",
    envvar="SKILLFORGE_REGISTRY_URL",
    help="Custom SkillForge registry API URL.",
)
@click.option(
    "--verbose", "-v", is_flag=True, help="Enable verbose output."
)
@click.pass_context
def cli(ctx: click.Context, registry_url: Optional[str], verbose: bool) -> None:
    """🔧 SkillForge — the open-source MCP skill pack manager.

    Scaffold, validate, install, publish, search, and list AI coding skills.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    if registry_url:
        ctx.obj["registry_url"] = registry_url
        set_config_value("registry_url", registry_url)
    else:
        config = load_config()
        ctx.obj["registry_url"] = config["registry_url"]


# ═══════════════════════════════════════════════════════════════════════════════
# init — scaffold a new SKILL.md
# ═══════════════════════════════════════════════════════════════════════════════

@cli.command()
@click.argument("name")
@click.option(
    "--output", "-o",
    default=".",
    type=click.Path(file_okay=False, writable=True),
    help="Directory to create SKILL.md in (default: current directory).",
)
@click.option(
    "--force", "-f", is_flag=True,
    help="Overwrite existing SKILL.md if present.",
)
@click.pass_context
def init(ctx: click.Context, name: str, output: str, force: bool) -> None:
    """Scaffold a new SKILL.md for a skill called NAME.

    Creates a SKILL.md file with YAML frontmatter and a Markdown body
    pre-populated with useful sections.

    \b
    Examples:
        skillforge init my-cool-skill
        skillforge init my-skill --output ./skills/
    """
    out_dir = Path(output).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    skill_path = out_dir / "SKILL.md"

    if skill_path.exists() and not force:
        raise click.ClickException(
            f"SKILL.md already exists at {skill_path}. Use --force to overwrite."
        )

    title = name.replace("-", " ").replace("_", " ").title()
    content = SKILL_MD_TEMPLATE.format(name=name, title=title)

    skill_path.write_text(content, encoding="utf-8")

    console.print(
        Panel.fit(
            f"[bold green]✓[/bold green] Created [bold]{skill_path}[/bold]\n\n"
            f"[dim]Name:[/dim] [cyan]{name}[/cyan]\n"
            f"[dim]Size:[/dim] {len(content)} bytes\n\n"
            f"Edit the file to fill in your skill details, then run:\n"
            f"  [bold]skillforge validate {skill_path}[/bold]\n"
            f"  [bold]skillforge publish {skill_path}[/bold]",
            title="Skill Scaffolded",
            border_style="green",
        )
    )


# ═══════════════════════════════════════════════════════════════════════════════
# validate — check SKILL.md correctness
# ═══════════════════════════════════════════════════════════════════════════════

@cli.command()
@click.argument(
    "path",
    default="SKILL.md",
    type=click.Path(exists=True, dir_okay=False),
)
@click.pass_context
def validate(ctx: click.Context, path: str) -> None:
    """Validate a SKILL.md file.

    Checks YAML frontmatter structure, required fields, version format,
    and other schema rules. Prints a friendly report.

    \b
    Examples:
        skillforge validate
        skillforge validate ./my-skill/SKILL.md
    """
    filepath = Path(path).resolve()
    content = _read_skill_file(filepath)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console,
    ) as progress:
        progress.add_task(description="[cyan]Parsing and validating...", total=None)

        try:
            skill = parse_skill_md(content)
        except (ValueError, yaml.YAMLError) as e:
            console.print(f"[bold red]✗[/bold red] Parse error: {e}")
            raise SystemExit(1)

        errors = validate_skill(skill)

    _show_validation_results(filepath, errors, skill.body)

    if errors:
        raise SystemExit(1)


# ═══════════════════════════════════════════════════════════════════════════════
# install — fetch and store a skill locally
# ═══════════════════════════════════════════════════════════════════════════════

@cli.command()
@click.argument("skill")
@click.option(
    "--from-file", "-f",
    type=click.Path(exists=True, dir_okay=False),
    help="Install from a local SKILL.md file instead of the registry.",
)
@click.pass_context
def install(ctx: click.Context, skill: str, from_file: Optional[str]) -> None:
    """Install a skill into the local skills directory.

    By default, fetches SKILL from the registry. Use --from-file to
    install from a local SKILL.md path.

    Skills are installed to ~/.skillforge/skills/<skill-name>/

    \b
    Examples:
        skillforge install weather-skill
        skillforge install --from-file ./SKILL.md
    """
    skills_dir = get_skills_dir()

    if from_file:
        # Local file install
        src = Path(from_file).resolve()
        content = _read_skill_file(src)

        try:
            parsed = parse_skill_md(content)
        except (ValueError, yaml.YAMLError) as e:
            raise click.ClickException(f"Failed to parse {src}: {e}")

        name = parsed.manifest.name
        dest_dir = skills_dir / name

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
            console=console,
        ) as progress:
            progress.add_task(
                description=f"[cyan]Installing {name} from local file...",
                total=None,
            )

            if dest_dir.exists():
                shutil.rmtree(dest_dir)
            dest_dir.mkdir(parents=True)

            shutil.copy2(src, dest_dir / "SKILL.md")

        console.print(
            Panel.fit(
                f"[bold green]✓[/bold green] Installed [bold cyan]{name}[/bold cyan] "
                f"v{parsed.manifest.version}\n\n"
                f"[dim]Location:[/dim] {dest_dir}\n"
                f"[dim]Files:[/dim] SKILL.md",
                title="Install Complete",
                border_style="green",
            )
        )
    else:
        # Registry install
        client = _get_registry_client(ctx)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
            console=console,
        ) as progress:
            progress.add_task(
                description=f"[cyan]Fetching {skill} from registry...",
                total=None,
            )

            data = client.get_skill(skill)

        if not data:
            # Fall back: try interpreting as a name and do a local install from cwd
            local_skill = Path(skill)
            if local_skill.exists():
                console.print(
                    f"[yellow]![/yellow] Not found in registry, "
                    f"treating as local file: {local_skill}"
                )
                ctx.invoke(install, skill=skill, from_file=str(local_skill))
                return

            raise click.ClickException(
                f"Skill '{skill}' not found in registry. "
                f"Use --from-file to install from a local SKILL.md."
            )

        name = data.get("name", skill)
        dest_dir = skills_dir / name
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Write the raw SKILL.md content if available, or reconstruct from metadata
        if "raw" in data or "body" in data:
            md_path = dest_dir / "SKILL.md"
            md_path.write_text(
                data.get("raw", data.get("body", "")), encoding="utf-8"
            )

        # Store metadata
        meta_path = dest_dir / "metadata.json"
        meta_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

        console.print(
            Panel.fit(
                f"[bold green]✓[/bold green] Installed [bold cyan]{name}[/bold cyan] "
                f"v{data.get('version', '?')}\n\n"
                f"[dim]Description:[/dim] {data.get('description', 'N/A')}\n"
                f"[dim]Location:[/dim] {dest_dir}",
                title="Install Complete",
                border_style="green",
            )
        )


# ═══════════════════════════════════════════════════════════════════════════════
# list — show installed skills
# ═══════════════════════════════════════════════════════════════════════════════

@cli.command("list")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
@click.pass_context
def list_skills(ctx: click.Context, as_json: bool) -> None:
    """List all locally installed skills.

    \b
    Examples:
        skillforge list
        skillforge list --json
    """
    skills_dir = get_skills_dir()

    skills = []
    if skills_dir.exists():
        for item in sorted(skills_dir.iterdir()):
            if item.is_dir():
                skill_md = item / "SKILL.md"
                meta = item / "metadata.json"

                info: dict[str, str | None] = {
                    "name": item.name,
                    "version": "?",
                    "description": None,
                    "path": str(item),
                }

                if skill_md.exists():
                    try:
                        parsed = parse_skill_md(skill_md.read_text(encoding="utf-8"))
                        info["version"] = str(parsed.version)
                        info["description"] = parsed.manifest.description
                    except (ValueError, yaml.YAMLError):
                        pass
                elif meta.exists():
                    try:
                        mdata = json.loads(meta.read_text(encoding="utf-8"))
                        info["version"] = mdata.get("version", "?")
                        info["description"] = mdata.get("description")
                    except (json.JSONDecodeError):
                        pass

                skills.append(info)

    if as_json:
        console.print_json(json.dumps(skills, indent=2))
        return

    if not skills:
        console.print("[dim]No skills installed yet.[/dim]")
        console.print(f"[dim]Run [bold]skillforge install <name>[/bold] to get started.[/dim]")
        return

    table = Table(title="Installed Skills", border_style="cyan")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Version", style="green")
    table.add_column("Description", style="dim")

    for s in skills:
        desc = s["description"] or ""
        if len(desc) > 80:
            desc = desc[:77] + "..."
        table.add_row(s["name"], s["version"] or "?", desc)

    console.print(table)
    console.print(f"\n[dim]{len(skills)} skill(s) installed in {skills_dir}[/dim]")


# ═══════════════════════════════════════════════════════════════════════════════
# search — query the registry
# ═══════════════════════════════════════════════════════════════════════════════

@cli.command()
@click.argument("query")
@click.option("--limit", "-n", default=20, help="Max results (default: 20).")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
@click.pass_context
def search(ctx: click.Context, query: str, limit: int, as_json: bool) -> None:
    """Search the SkillForge registry for skills.

    \b
    Examples:
        skillforge search weather
        skillforge search "image generation" --limit 5
        skillforge search git --json
    """
    client = _get_registry_client(ctx)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console,
    ) as progress:
        progress.add_task(
            description=f"[cyan]Searching for '{query}'...",
            total=None,
        )
        results = client.search(query, limit=limit)

    if as_json:
        console.print_json(json.dumps(results, indent=2))
        return

    if not results:
        # Fall back: search local installed skills
        local_results = _search_local(query)

        if local_results:
            console.print(
                f"[yellow]![/yellow] No registry results, "
                f"showing [bold]{len(local_results)}[/bold] local match(es):"
            )
            table = Table(title=f'Local matches for "{query}"', border_style="yellow")
            table.add_column("Name", style="cyan")
            table.add_column("Version", style="green")
            table.add_column("Description", style="dim")

            for r in local_results:
                desc = r.get("description") or ""
                if len(desc) > 80:
                    desc = desc[:77] + "..."
                table.add_row(r["name"], r.get("version", "?"), desc)

            console.print(table)
        else:
            console.print(
                f"[dim]No results found for '[bold]{query}[/bold]' "
                f"in the registry or locally.[/dim]"
            )
        return

    table = Table(title=f'Search results for "{query}"', border_style="cyan")
    table.add_column("Name", style="cyan")
    table.add_column("Version", style="green")
    table.add_column("Description", style="dim")
    table.add_column("Downloads", justify="right")

    for r in results:
        desc = r.get("description") or ""
        if len(desc) > 70:
            desc = desc[:67] + "..."
        table.add_row(
            r.get("name", "?"),
            r.get("version", "?"),
            desc,
            str(r.get("download_count", 0)),
        )

    console.print(table)
    console.print(f"\n[dim]{len(results)} result(s) from {client.base_url}[/dim]")


def _search_local(query: str) -> list[dict[str, str | None]]:
    """Search locally installed skills for a query match."""
    skills_dir = get_skills_dir()
    results = []

    if not skills_dir.exists():
        return results

    q = query.lower()
    for item in sorted(skills_dir.iterdir()):
        if not item.is_dir():
            continue

        skill_md = item / "SKILL.md"
        name = item.name
        desc: str | None = None
        version: str | None = None

        if skill_md.exists():
            try:
                parsed = parse_skill_md(skill_md.read_text(encoding="utf-8"))
                version = str(parsed.version)
                desc = parsed.manifest.description
            except (ValueError, yaml.YAMLError):
                pass

        # Match on name, description, or tags
        if (
            q in name.lower()
            or (desc and q in desc.lower())
        ):
            results.append({
                "name": name,
                "version": version,
                "description": desc,
            })

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# publish — validate and upload to registry
# ═══════════════════════════════════════════════════════════════════════════════

@cli.command()
@click.argument(
    "path",
    default="SKILL.md",
    type=click.Path(exists=True, dir_okay=False),
)
@click.option(
    "--dry-run", is_flag=True,
    help="Validate only; do not actually publish.",
)
@click.pass_context
def publish(ctx: click.Context, path: str, dry_run: bool) -> None:
    """Publish a SKILL.md to the SkillForge registry.

    Validates the skill first. If valid, uploads it to the registry.

    \b
    Examples:
        skillforge publish
        skillforge publish ./my-skill/SKILL.md
        skillforge publish --dry-run
    """
    filepath = Path(path).resolve()
    content = _read_skill_file(filepath)

    # Parse and validate
    try:
        skill = parse_skill_md(content)
    except (ValueError, yaml.YAMLError) as e:
        raise click.ClickException(f"Parse error: {e}")

    errors = validate_skill(skill)

    if errors:
        _show_validation_results(filepath, errors, skill.body)
        raise click.ClickException(
            "Validation failed. Fix the errors above before publishing."
        )

    console.print(f"[green]✓[/green] Validation passed for {filepath}")

    if dry_run:
        console.print(
            Panel.fit(
                "[bold yellow]Dry run[/bold yellow] — would publish:\n\n"
                f"[dim]Name:[/dim] [cyan]{skill.manifest.name}[/cyan]\n"
                f"[dim]Version:[/dim] [green]{skill.manifest.version}[/green]\n"
                f"[dim]Description:[/dim] {skill.manifest.description}\n",
                title="Publish (Dry Run)",
                border_style="yellow",
            )
        )
        return

    # Upload
    client = _get_registry_client(ctx)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console,
    ) as progress:
        progress.add_task(
            description=f"[cyan]Publishing {skill.manifest.name}...",
            total=None,
        )

        try:
            payload = {
                "name": skill.manifest.name,
                "version": skill.manifest.version,
                "description": skill.manifest.description,
                "author": skill.manifest.author,
                "license": skill.manifest.license,
                "tags": skill.manifest.tags,
                "homepage": skill.manifest.homepage,
                "repository": skill.manifest.repository,
                "icon": skill.manifest.icon,
                "raw": content,
            }
            result = client.publish(payload)
        except Exception as e:
            raise click.ClickException(f"Failed to publish: {e}")

    console.print(
        Panel.fit(
            f"[bold green]✓[/bold green] Published [bold cyan]{skill.manifest.name}[/bold cyan] "
            f"v{skill.manifest.version}\n\n"
            f"[dim]Registry:[/dim] {client.base_url}\n"
            f"[dim]ID:[/dim] {result.get('id', '?')}",
            title="Publish Complete",
            border_style="green",
        )
    )


if __name__ == "__main__":
    cli()
