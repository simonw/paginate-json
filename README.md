# paginate-json

[![PyPI](https://img.shields.io/pypi/v/paginate-json.svg)](https://pypi.python.org/pypi/paginate-json)
[![Changelog](https://img.shields.io/github/v/release/simonw/paginate-json?include_prereleases&label=changelog)](https://github.com/simonw/paginate-json/releases)
[![Tests](https://github.com/simonw/paginate-json/workflows/Test/badge.svg)](https://github.com/simonw/paginate-json/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/paginate-json/blob/main/LICENSE)

CLI tool for retrieving JSON from paginated APIs.

Examples:

- [Combined release notes from GitHub with jq and paginate-json](https://til.simonwillison.net/jq/combined-github-release-notes)
- [Export a Mastodon timeline to SQLite](https://til.simonwillison.net/mastodon/export-timeline-to-sqlite)

Currently works against APIs that use the HTTP Link header for pagination. The GitHub API is [the most obvious example](https://developer.github.com/v3/guides/traversing-with-pagination/).

    Usage: paginate-json [OPTIONS] URL

      Fetch paginated JSON from a URL

    Options:
      --version                Show the version and exit.
      --nl                     Output newline-delimited JSON
      --jq TEXT                jq transformation to run on each page
      --accept TEXT            Accept header to send
      --sleep INTEGER          Seconds to delay between requests
      --silent                 Don't show progress on stderr
      --show-headers           Dump response headers out to stderr
      --header <TEXT TEXT>...  Send custom request headers
      --help                   Show this message and exit.

The `--jq` option only works if you install the optional pyjq dependency.

Works well in conjunction with [sqlite-utils](https://github.com/simonw/sqlite-utils). For example, here's how to load all of the GitHub issues for a project into a local SQLite database.
```bash
paginate-json \
  "https://api.github.com/repos/simonw/datasette/issues?state=all&filter=all" \
  --nl | \
  sqlite-utils upsert /tmp/issues.db issues - --nl --pk=id
```
You can then use [other features of sqlite-utils](https://sqlite-utils.readthedocs.io/en/latest/cli.html) to enhance the resulting database. For example, to enable full-text search on the issue title and body columns:
```bash
sqlite-utils enable-fts /tmp/issues.db issues title body
```
You can use the `--header` option to send additional request headers. For example, if you have a GitHub OAuth token you can pass it like this:
```bash
paginate-json https://api.github.com/users/simonw/events \
  --header Authorization "bearer e94d9e404d86..."
```
