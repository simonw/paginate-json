import click
import requests
import json
import textwrap
import time

try:
    import jq as pyjq
except ImportError:
    try:
        import pyjq
    except ImportError:
        pyjq = None


@click.command()
@click.version_option()
@click.argument("url", type=str, required=True)
@click.option("--nl", help="Output newline-delimited JSON", is_flag=True)
@click.option("--key", help="Top-level key to extract from each page")
@click.option("--jq", help="jq transformation to run on each page")
@click.option("--accept", help="Accept header to send")
@click.option("--sleep", help="Seconds to delay between requests", type=int)
@click.option("--silent", help="Don't show progress on stderr - default", is_flag=True)
@click.option("-v", "--verbose", help="Show progress on stderr", is_flag=True)
@click.option(
    "--show-headers", help="Dump response headers out to stderr", is_flag=True
)
@click.option(
    "--ignore-http-errors", help="Keep going on non-200 HTTP status codes", is_flag=True
)
@click.option(
    "--header", type=(str, str), multiple=True, help="Send custom request headers"
)
def cli(
    url,
    nl,
    key,
    jq,
    accept,
    sleep,
    silent,
    verbose,
    show_headers,
    ignore_http_errors,
    header,
):
    """
    Fetch paginated JSON from a URL

    Example usage:

    \b
        paginate-json https://api.github.com/repos/simonw/datasette/issues
    """
    # --silent is only in here for backwards compatibility
    silent = not verbose
    if jq and not pyjq:
        raise click.ClickException(
            "Missing dependency: 'pip install pyjq' for this to work"
        )
    if key and jq:
        raise click.ClickException("Can't use --key and --jq together")
    headers = {}
    for header_name, header_value in header:
        headers[header_name] = header_value
    if nl:
        for chunk in paginate(
            url=url,
            jq=jq,
            key=key,
            accept=accept,
            sleep=sleep,
            silent=silent,
            show_headers=show_headers,
            ignore_http_errors=ignore_http_errors,
            headers=headers,
        ):
            if not isinstance(chunk, list):
                chunk = [chunk]
            for row in chunk:
                click.echo(json.dumps(row))
    else:
        def iter_all():
            for chunk in paginate(
                url=url,
                jq=jq,
                key=key,
                accept=accept,
                sleep=sleep,
                silent=silent,
                show_headers=show_headers,
                ignore_http_errors=ignore_http_errors,
                headers=headers,
            ):
                if not isinstance(chunk, list):
                    chunk = [chunk]
                yield from chunk

        # Output JSON array by starting with '['
        # Then iterate two at a time to detect the last one
        first = True
        for item, last in enumerate_last(iter_all()):
            if first:
                # Output after first successful HTTP request, to
                # avoid outputting '[' if the first request fails
                click.echo("[")
                first = False
            click.echo(
                textwrap.indent(
                    json.dumps(item, indent=2).rstrip() + ("" if last else ","), "  "
                )
            )
        # Output closing ']'
        click.echo("]")


def paginate(
    *,
    url,
    jq=None,
    key=None,
    accept=None,
    sleep=None,
    silent=False,
    show_headers=False,
    ignore_http_errors=False,
    headers=None,
):
    while url:
        if not silent:
            click.echo(url, err=True)
        headers = headers or {}
        if accept is not None:
            headers["Accept"] = accept
        response = requests.get(url, headers=headers)
        if response.status_code != 200 and not ignore_http_errors:
            raise click.ClickException(
                "{} error fetching {}".format(response.status_code, url)
            )
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
        if key:
            yield response.json()[key]
        elif jq:
            yield pyjq.first(jq, response.json())
        else:
            yield response.json()
        if sleep is not None:
            time.sleep(sleep)


def enumerate_last(iterable):
    it = iter(iterable)
    try:
        last = next(it)
    except StopIteration:
        return
    while True:
        try:
            current = next(it)
            yield last, False
            last = current
        except StopIteration:
            yield last, True
            break
