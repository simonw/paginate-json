from paginate_json import cli
from click.testing import CliRunner
import pytest


def test_pyjq_error():
    result = CliRunner().invoke(cli.cli, ["--jq=.", "http://example.com/"])
    assert 0 != result.exit_code
    assert (
        "Error: Missing dependency: 'pip install pyjq' for this to work"
        == result.output.strip()
    )


@pytest.mark.parametrize("relative_urls", (False, True))
def test_paginate_json(requests_mock, relative_urls):
    requests_mock.get(
        "https://example.com/",
        json=[1, 2],
        headers={
            "link": '<{}>; rel="next"'.format(
                "/?page=2" if relative_urls else "https://example.com/?page=2"
            )
        },
    )
    requests_mock.get("https://example.com/?page=2", json=[3, 4])
    result = CliRunner(mix_stderr=False).invoke(cli.cli, ["https://example.com/"])
    assert 0 == result.exit_code
    assert "[\n  1,\n  2,\n  3,\n  4\n]\n" == result.stdout
    assert "https://example.com/\nhttps://example.com/?page=2\n" == result.stderr


def test_header(requests_mock):
    requests_mock.get("https://example.com/", json=[1, 2])
    result = CliRunner(mix_stderr=False).invoke(
        cli.cli,
        ["https://example.com/", "--header", "foo", "bar", "--header", "baz", "1"],
    )
    assert 0 == result.exit_code
    assert "[\n  1,\n  2\n]\n" == result.stdout
    assert "https://example.com/\n" == result.stderr
    sent_request = requests_mock.request_history[0]
    assert "bar" == dict(sent_request.headers)["foo"]
    assert "1" == dict(sent_request.headers)["baz"]
