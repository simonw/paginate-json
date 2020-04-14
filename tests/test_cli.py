from paginate_json import cli
from click.testing import CliRunner


def test_pyjq_error():
    result = CliRunner().invoke(cli.cli, ["--jq=.", "http://example.com/"])
    assert 0 != result.exit_code
    assert (
        "Error: Missing dependency: 'pip install pyjq' for this to work"
        == result.output.strip()
    )


def test_paginate_json(requests_mock):
    requests_mock.get(
        "https://example.com/",
        json=[1, 2],
        headers={"link": '<https://example.com/?page=2>; rel="next"'},
    )
    requests_mock.get("https://example.com/?page=2", json=[3, 4])
    result = CliRunner(mix_stderr=False).invoke(cli.cli, ["https://example.com/"])
    assert 0 == result.exit_code
    assert "[\n  1,\n  2,\n  3,\n  4\n]\n" == result.stdout
    assert "https://example.com/\nhttps://example.com/?page=2\n" == result.stderr
