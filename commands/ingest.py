"""Ingest command - Add documents to the knowledge base."""

import click
import httpx
from pathlib import Path
from cli.config import get_api_url


@click.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--directory",
    "-d",
    is_flag=True,
    help="Treat PATH as a directory containing markdown files",
)
@click.option("--api-url", default=None, help="Override API URL")
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
def ingest(path: str, directory: bool, api_url: str, verbose: bool):
    """Ingest documents from PATH into the knowledge base.

    PATH can be:
    - A markdown file (.md)
    - A directory containing markdown files (with --directory)

    Examples:

        openmedica ingest ./research/notes.md

        openmedica ingest ./docs --directory
    """
    base_url = api_url or get_api_url()

    with httpx.Client(timeout=60.0) as client:
        if directory:
            result = _ingest_directory(client, base_url, Path(path), verbose)
        else:
            result = _ingest_file(client, base_url, Path(path), verbose)

    if result.get("status") == "ingested":
        click.echo(f"Document ingested: {result['id']}")
    elif result.get("total"):
        click.echo(f"Ingested {result['succeeded']}/{result['total']} documents")
        if result.get("failed", 0) > 0:
            click.echo(f"Failed: {result['failed']}", err=True)
    else:
        click.echo(f"Ingestion failed: {result}", err=True)
        raise click.Exit(1)


def _ingest_file(client: httpx.Client, base_url: str, path: Path, verbose: bool):
    """Ingest a single file."""
    if verbose:
        click.echo(f"Reading {path}...")

    content = path.read_text(encoding="utf-8")

    if verbose:
        click.echo(f"Sending to API...")

    response = client.post(
        f"{base_url}/documents/ingest",
        data={"content": content},
    )
    response.raise_for_status()
    return response.json()


def _ingest_directory(
    client: httpx.Client, base_url: str, directory: Path, verbose: bool
):
    """Ingest all markdown files in a directory."""
    md_files = list(directory.rglob("*.md"))

    if not md_files:
        click.echo(f"No markdown files found in {directory}")
        return {"status": "no_files"}

    if verbose:
        click.echo(f"Found {len(md_files)} markdown files")

    response = client.post(
        f"{base_url}/documents/ingest-directory",
        data={"directory": str(directory)},
    )
    response.raise_for_status()
    return response.json()
