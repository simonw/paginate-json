# paginate-json

[![PyPI](https://img.shields.io/pypi/v/paginate-json.svg)](https://pypi.python.org/pypi/paginate-json)
[![CircleCI](https://circleci.com/gh/simonw/paginate-json.svg?style=svg)](https://circleci.com/gh/simonw/paginate-json)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/paginate-json/blob/master/LICENSE)

CLI tool for retrieving JSON from paginated APIs.

Currently works against APIs that use the HTTP Link header for pagination. The GitHub API is [the most obvious example](https://developer.github.com/v3/guides/traversing-with-pagination/).

    $ paginate-json --help
    Usage: paginate-json [OPTIONS] URL

      Fetch paginated JSON from a URL

    Options:
      --version      Show the version and exit.
      --nl           Output newline-delimited JSON
      --jq TEXT      jq transformation to run on each page
      --accept TEXT  Accept header to send
      --help         Show this message and exit.

The `--jq` option only works if you install the optional pyjq dependency.

Works well in conjunction with [sqlite-utils](https://github.com/simonw/sqlite-utils). For example, here's how to load all of the GitHub issues for a project into a local SQLite database.

    paginate-json \
        "https://api.github.com/repos/simonw/datasette/issues?state=all&filter=all" \
        --nl | \
        sqlite-utils upsert /tmp/issues.db issues - --nl --pk=id

You can then use [other features of sqlite-utils](https://sqlite-utils.readthedocs.io/en/latest/cli.html) to enhance the resulting database. For example, to enable full-text search on the issue title and body columns:

    sqlite-utils enable-fts /tmp/issues.db issues title body
