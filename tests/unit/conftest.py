"""Pytest configuration for unit tests"""

# pylint: disable=C0116,W0621
from unittest.mock import MagicMock, patch
import pytest
import click
from es_fieldusage.main import FieldUsage


# Fixture for mocking FieldUsage
@pytest.fixture
def mock_field_usage():
    field_usage = MagicMock(spec=FieldUsage)
    field_usage.report = {'accessed': {'field1': 1}, 'unaccessed': {'field2': 0}}
    field_usage.per_index_report = {
        'index1': {'accessed': {'field1': 1}, 'unaccessed': {'field2': 0}}
    }
    return field_usage


# Fixture for Click context
@pytest.fixture
def click_context():
    ctx = MagicMock(spec=click.Context)
    ctx.obj = {'configdict': {}}
    return ctx


@pytest.fixture
def mock_client():
    client = MagicMock()
    client.indices.field_usage_stats.return_value = {
        "index1": {"shards": [{"stats": {"fields": {"field1": {"any": 10}}}}]},
        "_shards": {},
    }
    client.indices.get_mapping.return_value = {
        "index1": {"mappings": {"properties": {"field1": {}}}}
    }
    return client


@pytest.fixture
def field_usage_instance(mock_client):
    with patch("es_fieldusage.main.get_client", return_value=mock_client):
        return FieldUsage(configdict={}, search_pattern="*")
