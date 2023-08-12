import click
import requests
import json
import time


try:
    import pyjq
except ImportError:
    pyjq = None


@click.command()
@click.version_option()
@click.argument("url", type=str, required=True)
@click.option("--nl", help="Output newline-delimited JSON", is_flag=True)
@click.option("--jq", help="jq transformation to run on each page")
@click.option("--accept", help="Accept header to send")
@click.option("--sleep", help="Seconds to delay between requests", type=int)
@click.option("--silent", help="Don't show progress on stderr", is_flag=True)
@click.option(
    "--show-headers", help="Dump response headers out to stderr", is_flag=True
)
@click.option(
    "--header", type=(str, str), multiple=True, help="Send custom request headers"
)
def cli(url, nl, jq, accept, sleep, silent, show_headers, header):
    """
    Fetch paginated JSON from a URL
    """
    if jq and not pyjq:
        raise click.ClickException(
            "Missing dependency: 'pip install pyjq' for this to work"
        )
    headers = {}
    for header_name, header_value in header:
        headers[header_name] = header_value
    if nl:
        for chunk in paginate(url, jq, accept, sleep, silent, show_headers, headers):
            if not silent:
                click.echo(len(chunk), err=True)
            for row in chunk:
                click.echo(json.dumps(row))
    else:
        all = []
        for chunk in paginate(url, jq, accept, sleep, silent, show_headers, headers):
            all.extend(chunk)
        click.echo(json.dumps(all, indent=2))


def paginate(
    url, jq, accept=None, sleep=None, silent=False, show_headers=False, headers=None
):
    while url:
        if not silent:
            click.echo(url, err=True)
        headers = headers or {}
        if accept is not None:
            headers["Accept"] = accept
        response = requests.get(url, headers=headers)
        if show_headers:
            click.echo(
                json.dumps(dict(response.headers), indent=4, default=repr), err=True
            )
        try:
            next = response.links.get("next").get("url")
            # Resolve a potentially-relative URL to an absolute URL
            url = requests.compat.urljoin(url, next)
        except AttributeError:
            url = None
        if jq:
            yield pyjq.first(jq, response.json())
        else:
            yield response.json()
        if sleep is not None:
            time.sleep(sleep)
