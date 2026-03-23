"""OpenMedica CLI - Main entry point."""

import click
from cli.commands.ingest import ingest
from cli.commands.search import search


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """OpenMedica CLI - Clinical evidence search for AI agents.

    This CLI provides tools for physicians and researchers to access
    clinical evidence through AI agents. All tools are research tools
    — NOT clinical decision support.

    Environment Variables:
        OPENMEDICA_API_URL    API base URL (default: http://localhost:8000/api/v1)
        OPENMEDICA_DOCS_DIR   Default documents directory

    Examples:

        # Ingest a document
        openmedica ingest ./research/notes.md
        openmedica ingest ./docs --directory

        # Search for clinical evidence
        openmedica search "diabetes treatment"
        openmedica search "cardiovascular" --category research

        # Get help
        openmedica --help
        openmedica ingest --help
        openmedica search --help
    """
    pass


cli.add_command(ingest)
cli.add_command(search)


if __name__ == "__main__":
    cli()
