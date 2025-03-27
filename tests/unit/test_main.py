"""Unit tests for main.py"""

# pylint: disable=C0116


def test_init(field_usage_instance):
    assert field_usage_instance.usage_stats
    assert field_usage_instance.indices == "index1"


def test_get(field_usage_instance):
    assert "index1" in field_usage_instance.usage_stats
    assert field_usage_instance.usage_stats["index1"]["field1"] == 10


def test_get_field_mappings(field_usage_instance):
    mappings = field_usage_instance.get_field_mappings("index1")
    assert "field1" in mappings


def test_populate_values(field_usage_instance):
    data = {}
    result = field_usage_instance.populate_values("index1", data)
    assert result["field1"] == 10


def test_get_resultset(field_usage_instance):
    result = field_usage_instance.get_resultset("index1")
    assert result["field1"] == 10


def test_merge_results(field_usage_instance):
    result = field_usage_instance.merge_results("index1")
    assert result["field1"] == 10


def test_per_index_report(field_usage_instance):
    report = field_usage_instance.per_index_report
    assert "index1" in report
    assert "accessed" in report["index1"]
    assert "field1" in report["index1"]["accessed"]


def test_report(field_usage_instance):
    report = field_usage_instance.report
    assert "accessed" in report
    assert "field1" in report["accessed"]


def test_result(field_usage_instance):
    result = field_usage_instance.result()
    assert "field1" in result


def test_results_by_index(field_usage_instance):
    results = field_usage_instance.results_by_index
    assert "index1" in results
    assert "field1" in results["index1"]


def test_results(field_usage_instance):
    results = field_usage_instance.results
    assert "field1" in results


def test_indices(field_usage_instance):
    assert field_usage_instance.indices == "index1"


def test_sum_index_stats(field_usage_instance):
    field_usage = {
        "index1": {"shards": [{"stats": {"fields": {"field1": {"any": 5}}}}]}
    }
    result = field_usage_instance.sum_index_stats(field_usage, "index1")
    assert result["field1"] == 5
