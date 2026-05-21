"""Allow `python -m skillforge_cli` as an alternative to the `skillforge` entry point."""

from skillforge_cli.main import cli

if __name__ == "__main__":
    cli()
