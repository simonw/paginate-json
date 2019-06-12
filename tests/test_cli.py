from paginate_json import cli
from click.testing import CliRunner


def test_pyjq_error():
    result = CliRunner().invoke(cli.cli, ["--jq=.", "http://example.com/"])
    assert 0 != result.exit_code
    assert (
        "Error: Missing dependency: 'pip install pyjq' for this to work"
        == result.output.strip()
    )
