"""Unit tests for commands.py"""

# pylint: disable=C0116
from unittest.mock import patch
from es_fieldusage.commands import (
    get_per_index,
    format_delimiter,
    header_msg,
    is_docker,
    output_generator,
    printout,
    override_filepath,
    FILEPATH_OVERRIDE,
)


def test_get_per_index_per_index_true(mock_field_usage):
    result = get_per_index(mock_field_usage, True)
    assert result == {
        'index1': {'accessed': {'field1': 1}, 'unaccessed': {'field2': 0}}
    }


def test_get_per_index_per_index_false(mock_field_usage):
    result = get_per_index(mock_field_usage, False)
    assert result == {
        'all_indices': {'accessed': {'field1': 1}, 'unaccessed': {'field2': 0}}
    }


# def test_get_per_index_exception(mock_field_usage):
#     mock_field_usage.per_index_report.return_value = 123.456
#     with patch('logging.getLogger') as mock_logger:
#         with pytest.raises(FatalException):
#             get_per_index(mock_field_usage, True)
#         mock_logger.return_value.critical.assert_called_once_with(
#             'Unable to get per_index_report data: Test exception'
#         )


def test_format_delimiter():
    assert format_delimiter(':') == ': '
    assert format_delimiter('=') == ' = '
    assert format_delimiter(',') == ','
    assert format_delimiter(' ') == ' '


def test_header_msg():
    assert header_msg("Test message", True) == "Test message"
    assert header_msg("Test message", False) == ""


@patch('pathlib.Path.is_file')
def test_is_docker_dockerenv_exists(mock_is_file):
    mock_is_file.return_value = True
    assert is_docker() is True


@patch('pathlib.Path.is_file')
def test_is_docker_cgroup_docker(mock_is_file):
    mock_is_file.side_effect = [False, True]  # /.dockerenv, /proc/self/cgroup
    with patch('pathlib.Path.read_text', return_value="docker"):
        assert is_docker() is True


@patch('pathlib.Path.is_file')
def test_is_docker_not_in_docker(mock_is_file):
    mock_is_file.side_effect = [False, False]  # Neither condition met
    assert is_docker() is False


def test_output_generator_show_counts_true():
    data = {'field1': 1, 'field2': 2}
    gen = output_generator(data, True, ':')
    assert list(gen) == ['field1: 1\n', 'field2: 2\n']


def test_output_generator_show_counts_false():
    data = {'field1': 1, 'field2': 2}
    gen = output_generator(data, False, ':')
    assert list(gen) == ['field1\n', 'field2\n']


def test_output_generator_custom_delimiter():
    data = {'field1': 1}
    gen = output_generator(data, True, ',')
    assert list(gen) == ['field1,1\n']


def test_printout_show_counts_true(capsys):
    data = {'field1': 1, 'field2': 2}
    printout(data, True, ':')
    captured = capsys.readouterr()
    assert captured.out == 'field1: 1\nfield2: 2\n'


def test_printout_show_counts_false(capsys):
    data = {'field1': 1, 'field2': 2}
    printout(data, False, ':')
    captured = capsys.readouterr()
    assert captured.out == 'field1\nfield2\n'


@patch('es_fieldusage.commands.is_docker')
def test_override_filepath_in_docker(mock_is_docker):
    mock_is_docker.return_value = True
    assert override_filepath() == {'default': FILEPATH_OVERRIDE}


@patch('es_fieldusage.commands.is_docker')
def test_override_filepath_not_in_docker(mock_is_docker):
    mock_is_docker.return_value = False
    assert not override_filepath()


# def test_stdout_command(click_context, mock_field_usage):
#     runner = CliRunner()
#     with patch('es_fieldusage.main.FieldUsage', return_value=mock_field_usage):
#         result = runner.invoke(
#             stdout,
#             ['--show-report', '--show-accessed', '--show-unaccessed', 'test_pattern'],
#             obj=click_context,
#         )
#         assert result.exit_code == 0
#         assert 'Accessed Fields' in result.output
#         assert 'Unaccessed Fields' in result.output
#         assert 'field1: 1' in result.output
#         assert 'field2' in result.output


# def test_stdout_exception(click_context):
#     with patch(
#         'es_fieldusage.main.FieldUsage', side_effect=Exception("Test exception")
#     ):
#         runner = CliRunner()
#         with patch('logging.getLogger') as mock_logger:
#             result = runner.invoke(stdout, ['test_pattern'], obj=click_context)
#             assert result.exit_code != 0
#             mock_logger.return_value.critical.assert_called_once_with(
#                 'Exception encountered: Test exception'
#             )


# def test_file_command(click_context, mock_field_usage, tmp_path):
#     runner = CliRunner()
#     filepath = str(tmp_path)
#     with patch('es_fieldusage.main.FieldUsage', return_value=mock_field_usage):
#         result = runner.invoke(
#             file,
#             [
#                 '--show-accessed',
#                 '--show-unaccessed',
#                 '--per-index',
#                 f'--filepath={filepath}',
#                 '--prefix=test',
#                 '--suffix=txt',
#                 'test_pattern',
#             ],
#             obj=click_context,
#         )
#         assert result.exit_code == 0
#         assert 'Number of files written: 1' in result.output
#         assert os.path.exists(os.path.join(filepath, 'test-index1.txt'))
#         with open(os.path.join(
# filepath, 'test-index1.txt'), 'r', encoding='utf8') as f:
#             content = f.read()
#             assert 'field1: 1' in content
#             assert 'field2' in content


# def test_file_json_output(click_context, mock_field_usage, tmp_path):
#     runner = CliRunner()
#     filepath = str(tmp_path)
#     with patch('es_fieldusage.main.FieldUsage', return_value=mock_field_usage):
#         result = runner.invoke(
#             file,
#             [
#                 '--show-accessed',
#                 f'--filepath={filepath}',
#                 '--prefix=test',
#                 '--suffix=json',
#                 'test_pattern',
#             ],
#             obj=click_context,
#         )
#         assert result.exit_code == 0
#         with open(
#             os.path.join(filepath, 'test-all_indices.json'), 'r', encoding='utf8'
#         ) as f:
#             content = f.read()
#             assert '"field1": 1' in content


# def test_index_command(click_context, mock_field_usage, tmp_path):
#     runner = CliRunner()
#     os.chdir(tmp_path)
#     with patch('es_fieldusage.main.FieldUsage', return_value=mock_field_usage):
#         result = runner.invoke(
#             index,
#             ['--show-accessed', '--per-index',
# '--indexname=test_idx', 'test_pattern'],
#             obj=click_context,
#         )
#         assert result.exit_code == 0
#         with open('testing', 'r', encoding='utf8') as f:
#             content = f.read()
#             assert '"index": "index1"' in content
#             assert '"field": {"name": "field1", "count": 1}' in content


# def test_show_indices_command(click_context):
#     mock_client = MagicMock()
#     mock_client.cat.indices.return_value = [{'index': 'index1'}, {'index': 'index2'}]
#     with patch('es_client.helpers.config.get_client', return_value=mock_client):
#         runner = CliRunner()
#         result = runner.invoke(show_indices, ['test-*'], obj=click_context)
#         assert result.exit_code == 0
#         assert 'Search Pattern: test-*' in result.output
#         assert '2 Indices Found' in result.output
#         assert 'index1' in result.output
#         assert 'index2' in result.output
