"""
Tests for cloud execution
"""
from pathlib import Path
import pytest
from click.testing import CliRunner

from ploomber_cli.cli import cli


@pytest.fixture
def runid():
    return '7b795661-15ad-415b-be95-0cd9dbe8588e'


@pytest.fixture
def taskid():
    return 'c29b409e-cfff-45ff-bc3d-77206180e1c5'


def test_cloud_build():
    pass


def test_cloud_list():
    runner = CliRunner()
    result = runner.invoke(cli, ['cloud', 'list'], catch_exceptions=False)

    assert 'created_at' in result.output
    assert 'runid' in result.output
    assert 'status' in result.output
    assert result.exit_code == 0


def test_cloud_status(runid):
    runner = CliRunner()
    result = runner.invoke(cli, ['cloud', 'status', runid])
    out = result.output
    assert 'taskid' in out
    assert 'name' in out
    assert 'runid' in out
    assert 'status' in out
    assert result.exit_code == 0


def test_cloud_products():
    runner = CliRunner()
    result = runner.invoke(cli, ['cloud', 'products'])

    assert 'path' in result.output
    assert result.exit_code == 0


def test_cloud_download(tmp_directory):
    runner = CliRunner()
    result = runner.invoke(cli, ['cloud', 'download', '*.html'])

    assert 'Downloading' in result.output
    assert result.exit_code == 0


def test_cloud_logs(runid):
    runner = CliRunner()
    result = runner.invoke(cli, ['cloud', 'logs', runid])
    assert 'START OF LOGS FOR TASK' in result.output
    assert 'END OF LOGS FOR TASK' in result.output
    assert result.exit_code == 0


def test_cloud_abort(runid):
    runner = CliRunner()
    result = runner.invoke(cli, ['cloud', 'abort', runid])

    assert 'Aborted.' in result.output
    assert result.exit_code == 0


def test_cloud_data_list():
    runner = CliRunner()
    result = runner.invoke(cli, ['cloud', 'data'])

    assert result.exit_code == 0


def test_cloud_data_upload_delete(tmp_directory):
    Path('file.txt').write_text('some text')

    runner = CliRunner()
    result = runner.invoke(cli, ['cloud', 'data', '--upload', 'file.txt'])
    assert result.exit_code == 0

    result = runner.invoke(cli, ['cloud', 'data', '--delete', 'file.txt'])
    assert result.exit_code == 0
