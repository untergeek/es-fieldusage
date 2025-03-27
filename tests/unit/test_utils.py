"""Unit tests for the utils module."""

# pylint: disable=C0116
import pytest
from es_fieldusage.helpers.utils import (
    convert_mapping,
    detuple,
    get_value_from_path,
    iterate_paths,
    output_report,
    override_settings,
    passthrough,
    sort_by_name,
    sort_by_value,
    sum_dict_values,
)
from es_fieldusage.exceptions import ConfigurationException


def test_convert_mapping():
    data = {
        "field1": {"properties": {"subfield1": {}}},
        "field2": {"type": "text"},
    }
    expected = {"field1": {"subfield1": 0}, "field2": 0}
    assert convert_mapping(data) == expected


def test_detuple():
    assert detuple([(1, 2)]) == [1, 2]
    assert detuple([1]) == [1]


def test_get_value_from_path():
    data = {"a": {"b": {"c": 42}}}
    path = ["a", "b", "c"]
    assert get_value_from_path(data, path) == 42


def test_iterate_paths():
    data = {"a": {"b": {"c": 42}}, "d": 1}
    paths = list(iterate_paths(data))
    expected = [["a", "b", "c"], ["d"]]
    assert paths == expected


def test_output_report(capsys):
    report = {
        "indices": ["index1", "index2"],
        "field_count": 10,
        "accessed": {"field1": 1, "field2": 2},
        "unaccessed": {"field3": 0},
    }
    output_report("test_pattern", report)
    captured = capsys.readouterr()
    assert "Summary Report" in captured.out
    assert "test_pattern" in captured.out
    assert "2 Indices Found" in captured.out
    assert "Total Fields Found: 10" in captured.out
    assert "Accessed Fields: 2" in captured.out
    assert "Unaccessed Fields: 1" in captured.out


def test_override_settings():
    data = {"key1": "value1", "key2": "value2"}
    new_data = {"key1": "new_value1"}
    expected = {"key1": "new_value1", "key2": "value2"}
    assert override_settings(data, new_data) == expected

    with pytest.raises(ConfigurationException):
        override_settings(data, "not_a_dict")


def test_passthrough():
    def sample_func(*args, **kwargs):
        return args, kwargs

    wrapped = passthrough(sample_func)
    assert wrapped((1,), {"key": "value"}) == ((1,), {"key": "value"})


def test_sort_by_name():
    data = {"b": 2, "a": 1}
    expected = {"a": 1, "b": 2}
    assert sort_by_name(data) == expected


def test_sort_by_value():
    data = {"a": 1, "b": 2}
    expected = {"b": 2, "a": 1}
    assert sort_by_value(data) == expected


def test_sum_dict_values():
    data = {
        "dict1": {"a": 1, "b": 2},
        "dict2": {"a": 3, "c": 4},
    }
    expected = {"a": 4, "b": 2, "c": 4}
    assert sum_dict_values(data) == expected


@pytest.mark.parametrize(
    "search_pattern, report, expected_strings",
    [
        # Test case 1: Single index as string
        (
            "test_index",
            {
                "indices": "test_index",
                "field_count": 5,
                "accessed": {"field1": 1},
                "unaccessed": {"field2": 0},
            },
            [
                "Summary Report",
                "Search Pattern: test_index",
                "Index Found: test_index",
                "Total Fields Found: 5",
                "Accessed Fields: 1",
                "Unaccessed Fields: 1",
            ],
        ),
        # Test case 2: Single index as list
        (
            "test_index",
            {
                "indices": ["test_index"],
                "field_count": 5,
                "accessed": {"field1": 1},
                "unaccessed": {"field2": 0},
            },
            [
                "Summary Report",
                "Search Pattern: test_index",
                "1 Indices Found: ['test_index']",
                "Total Fields Found: 5",
                "Accessed Fields: 1",
                "Unaccessed Fields: 1",
            ],
        ),
        # Test case 3: Multiple indices (3)
        (
            "test_*",
            {
                "indices": ["index1", "index2", "index3"],
                "field_count": 15,
                "accessed": {"field1": 1, "field2": 2, "field3": 3},
                "unaccessed": {"field4": 0, "field5": 0},
            },
            [
                "Summary Report",
                "Search Pattern: test_*",
                "3 Indices Found: ['index1', 'index2', 'index3']",
                "Total Fields Found: 15",
                "Accessed Fields: 3",
                "Unaccessed Fields: 2",
            ],
        ),
        # Test case 4: Many indices (4)
        (
            "test_*",
            {
                "indices": ["index1", "index2", "index3", "index4"],
                "field_count": 20,
                "accessed": {"field1": 1, "field2": 2, "field3": 3, "field4": 4},
                "unaccessed": {"field5": 0, "field6": 0, "field7": 0},
            },
            [
                "Summary Report",
                "Search Pattern: test_*",
                "4 Indices Found: (data too big)",
                "Total Fields Found: 20",
                "Accessed Fields: 4",
                "Unaccessed Fields: 3",
            ],
        ),
        # Test case 5: No indices
        (
            "test_*",
            {
                "indices": [],
                "field_count": 0,
                "accessed": {},
                "unaccessed": {},
            },
            [
                "Summary Report",
                "Search Pattern: test_*",
                "0 Indices Found: []",
                "Total Fields Found: 0",
                "Accessed Fields: 0",
                "Unaccessed Fields: 0",
            ],
        ),
    ],
)
def test_output_report_extended(capsys, search_pattern, report, expected_strings):
    """Test output_report function for various report configurations."""
    output_report(search_pattern, report)
    captured = capsys.readouterr()
    for string in expected_strings:
        assert string in captured.out, f"Expected '{string}' in output:\n{captured.out}"
