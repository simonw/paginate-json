from paginate_json import cli
from click.testing import CliRunner
import pytest


@pytest.mark.skipif(cli.pyjq, reason="pyjq is installed")
def test_pyjq_error():
    result = CliRunner().invoke(cli.cli, ["--jq=.", "http://example.com/"])
    assert result.exit_code != 0
    assert (
        result.output.strip()
        == "Error: Missing dependency: 'pip install pyjq' for this to work"
    )


@pytest.mark.parametrize("relative_urls", (False, True))
def test_paginate_json(requests_mock, relative_urls):
    requests_mock.get(
        "https://example.com/",
        json=[{"id": 1}, {"id": 2}],
        headers={
            "link": '<{}>; rel="next"'.format(
                "/?page=2" if relative_urls else "https://example.com/?page=2"
            )
        },
    )
    requests_mock.get("https://example.com/?page=2", json=[{"id": 3}, {"id": 4}])
    result = CliRunner(mix_stderr=False).invoke(cli.cli, ["https://example.com/"])
    assert result.exit_code == 0
    assert result.stdout == (
        '[\n  {\n    "id": 1\n  },\n  {\n    "id": 2\n  },\n'
        '  {\n    "id": 3\n  },\n  {\n    "id": 4\n  }\n]\n'
    )


def test_paginate_json_key(requests_mock):
    requests_mock.get(
        "https://example.com/",
        json={"rows": [1, 2]},
        headers={"link": '</?page=2>; rel="next"'},
    )
    requests_mock.get("https://example.com/?page=2", json={"rows": [3, 4]})
    result = CliRunner(mix_stderr=False).invoke(
        cli.cli, ["https://example.com/", "--key", "rows"]
    )
    assert result.exit_code == 0
    assert result.stdout == "[\n  1,\n  2,\n  3,\n  4\n]\n"

@pytest.mark.skipif(not cli.pyjq, reason="pyjq is not installed")
def test_next_page_jq(requests_mock):
    requests_mock.get(
        "https://example.com",
        json={"rows": [{"id": 1}, {"id": 2}], "nextpage": "https://example.com/?page=2"}
    )
    requests_mock.get(
        "https://example.com/?page=2",
        json={"rows": [{"id": 3}, {"id": 4}]}
    )
    result = CliRunner(mix_stderr=False).invoke(
        cli.cli, ["https://example.com/", "--next", ".nextpage", "--key", "rows"]
    )
    assert result.exit_code == 0
    assert result.stdout == (
        '[\n  {\n    "id": 1\n  },\n  {\n    "id": 2\n  },\n'
        '  {\n    "id": 3\n  },\n  {\n    "id": 4\n  }\n]\n'
    )


@pytest.mark.skipif(not cli.pyjq, reason="pyjq is not installed")
def test_paginate_json_jq(requests_mock):
    requests_mock.get(
        "https://example.com/",
        json={"rows": [1, 2]},
        headers={"link": '</?page=2>; rel="next"'},
    )
    requests_mock.get("https://example.com/?page=2", json={"rows": [3, 4]})
    result = CliRunner(mix_stderr=False).invoke(
        cli.cli, ["https://example.com/", "--jq", ".rows"]
    )
    assert result.exit_code == 0
    assert result.stdout == "[\n  1,\n  2,\n  3,\n  4\n]\n"


def test_header(requests_mock):
    requests_mock.get("https://example.com/", json=[1, 2])
    result = CliRunner(mix_stderr=False).invoke(
        cli.cli,
        ["https://example.com/", "--header", "foo", "bar", "--header", "baz", "1"],
    )
    assert result.exit_code == 0
    assert result.stdout == "[\n  1,\n  2\n]\n"
    sent_request = requests_mock.request_history[0]
    assert dict(sent_request.headers)["foo"] == "bar"
    assert dict(sent_request.headers)["baz"] == "1"


@pytest.mark.parametrize("ignore_errors", (False, True))
def test_ignore_http_errors(requests_mock, ignore_errors):
    requests_mock.get("https://example.com/", json=[1, 2], status_code=500)
    result = CliRunner(mix_stderr=False).invoke(
        cli.cli,
        ["https://example.com/"] + (["--ignore-http-errors"] if ignore_errors else []),
    )
    assert result.exit_code == 0 if ignore_errors else 1
    if ignore_errors:
        assert result.stdout == "[\n  1,\n  2\n]\n"
    else:
        assert result.stdout == ""
        assert "500 error fetching" in result.stderr
