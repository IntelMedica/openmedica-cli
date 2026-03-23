"""Search command - Query clinical evidence across databases."""

import click
import httpx
import json
from cli.config import get_api_url


@click.command()
@click.argument("query")
@click.option(
    "--category", "-c", help="Filter by category (e.g., 'research', 'guidelines')"
)
@click.option(
    "--tags", "-t", help="Comma-separated tags to filter (e.g., 'diabetes,treatment')"
)
@click.option(
    "--limit",
    "-l",
    default=10,
    type=int,
    help="Maximum number of results (default: 10)",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "json", "simple"]),
    default="table",
    help="Output format",
)
@click.option("--api-url", help="Override API URL")
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show verbose output including scores and sources",
)
def search(
    query: str,
    category: str,
    tags: str,
    limit: int,
    format: str,
    api_url: str,
    verbose: bool,
):
    """Search clinical evidence across all databases.

    Examples:

        openmedica search "diabetes treatment options"

        openmedica search "cardiovascular risk" --category research

        openmedica search "drug interactions" --tags "pharmacology,interactions"

        openmedica search "clinical guidelines" --format json
    """
    base_url = api_url or get_api_url()

    params = {"q": query, "limit": limit}
    if category:
        params["category"] = category
    if tags:
        params["tags"] = tags

    if verbose:
        click.echo(f"Query: {query}")
        click.echo(f"API: {base_url}/search")

    with httpx.Client(timeout=30.0) as client:
        response = client.get(f"{base_url}/search", params=params)
        response.raise_for_status()
        result = response.json()

    _display_results(result, format, verbose)


def _display_results(result: dict, format: str, verbose: bool):
    """Display search results in specified format."""
    results = result.get("results", [])

    if not results:
        click.echo("No results found.")
        return

    if format == "json":
        click.echo(json.dumps(result, indent=2))
        return

    if format == "simple":
        for r in results:
            doc = r["document"]
            click.echo(f"\n{doc['title']}")
            content = (
                doc["content"][:200] + "..."
                if len(doc["content"]) > 200
                else doc["content"]
            )
            click.echo(content)
        return

    # Table format (default)
    click.echo(f"\n{'=' * 80}")
    click.echo(f"Search: {result.get('query', 'unknown')}")
    click.echo(f"Results: {len(results)} found")
    click.echo(f"{'=' * 80}\n")

    for i, r in enumerate(results, 1):
        doc = r["document"]
        score = r.get("score", 0)
        source = r.get("source", "unknown")

        click.echo(f"[{i}] {doc['title']}")

        if verbose:
            click.echo(f"    Score: {score:.3f} | Source: {source}")

        content = (
            doc["content"][:150] + "..."
            if len(doc["content"]) > 150
            else doc["content"]
        )
        click.echo(f"    {content}")

        if doc.get("category") or doc.get("tags"):
            meta = []
            if doc.get("category"):
                meta.append(f"category={doc['category']}")
            if doc.get("tags"):
                meta.append(f"tags={','.join(doc['tags'])}")
            click.echo(f"    ({'; '.join(meta)})")

        click.echo()
