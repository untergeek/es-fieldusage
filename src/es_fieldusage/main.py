"""Main app definition"""

import logging
from es_client.helpers.config import get_client
from es_fieldusage.helpers import utils as u
from es_fieldusage.exceptions import ResultNotExpected, ValueMismatch

# pylint: disable=R0902


class FieldUsage:
    """Main Class"""

    def __init__(self, configdict, search_pattern):
        self.logger = logging.getLogger(__name__)
        self.client = get_client(configdict=configdict)
        self.usage_stats = {}
        self.indices_data = []
        self.per_index_data = {}
        self.results_data = {}
        self.report_data = {}
        self.per_index_report_data = {}
        self.get(search_pattern)

    def get(self, search_pattern):
        """
        Get ``raw_data`` from the field_usage_stats API for all indices in
        ``search_pattern`` Iterate over ``raw_data`` to build ``self.usage_stats``
        """
        try:
            field_usage = self.client.indices.field_usage_stats(index=search_pattern)
        except Exception as exc:
            raise ResultNotExpected(f'Unable to get field usage: {exc}') from exc
        for index in list(field_usage.keys()):
            if index == '_shards':
                # Ignore this key as it is "global"
                continue
            self.usage_stats[index] = self.sum_index_stats(field_usage, index)

    def get_field_mappings(self, idx):
        """
        Return only the field mappings for index ``idx`` (not the entire index
        mapping)
        """
        return self.client.indices.get_mapping(index=idx)[idx]['mappings']['properties']

    def populate_values(self, idx, data):
        """Now add the field usage values for idx to data and return the result"""
        for field in list(self.usage_stats[idx].keys()):
            if '.' in field:
                path = tuple(field.split('.'))
            else:
                path = field
            data[path] = self.usage_stats[idx][field]
        return data

    def get_resultset(self, idx):
        """Populate a result set with the fields in the index mapping"""
        result = {}
        if idx in self.usage_stats:
            allfields = u.convert_mapping(self.get_field_mappings(idx))
            result = self.populate_values(idx, allfields)
        return result

    def merge_results(self, idx):
        """Merge field usage data with index mapping"""
        retval = {}
        data = self.get_resultset(idx)
        for path in u.iterate_paths(data):
            value = u.get_value_from_path(data, path)
            key = '.'.join(u.detuple(path))
            retval[key] = value
        return retval

    def verify_single_index(self, index=None):
        """
        Ensure the index count is 1 for certain methods
        If no index provided, and only one is in self.indices, use that one
        """
        if index is None:
            if isinstance(self.indices, list):
                if len(self.indices) > 1:
                    msg = (
                        f'Too many indices found. Indicate single index for result, '
                        f'or use results for all indices. Found: {self.indices}'
                    )
                    raise ValueMismatch(msg)
                if len(self.indices) < 1:
                    raise ValueMismatch('No indices found.')
            else:
                index = self.indices
        return index

    @property
    def per_index_report(self):
        """Generate summary report data"""
        if not self.per_index_report_data:
            self.report_data['indices'] = self.indices
            self.report_data['field_count'] = len(self.results.keys())
            for idx in list(self.results_by_index.keys()):
                self.per_index_report_data[idx] = {}
                self.per_index_report_data[idx]['accessed'] = {}
                self.per_index_report_data[idx]['unaccessed'] = {}
                for key, value in self.results_by_index[idx].items():
                    if value == 0:
                        self.per_index_report_data[idx]['unaccessed'][key] = value
                    else:
                        self.per_index_report_data[idx]['accessed'][key] = value
        return self.per_index_report_data

    @property
    def report(self):
        """Generate summary report data"""
        if not self.report_data:
            self.report_data['indices'] = self.indices
            self.report_data['field_count'] = len(self.results.keys())
            self.report_data['accessed'] = {}
            self.report_data['unaccessed'] = {}
            for key, value in self.results.items():
                if value == 0:
                    self.report_data['unaccessed'][key] = value
                else:
                    self.report_data['accessed'][key] = value
        return self.report_data

    def result(self, idx=None):
        """Return a single index result as a dictionary"""
        idx = self.verify_single_index(index=idx)
        return u.sort_by_value(self.merge_results(idx))

    @property
    def results_by_index(self):
        """
        Return all results as a dictionary, with the index name as the root key,
        and all stats for that index as the value, which is a dictionary generated
        by ``self.result()``.
        """
        if not self.per_index_data:
            if not isinstance(self.indices, list):
                idx_list = [self.indices]
            else:
                idx_list = self.indices
            for idx in idx_list:
                self.per_index_data[idx] = self.result(idx=idx)
        return self.per_index_data

    @property
    def results(self):
        """Return results for all indices found with values summed per mapping leaf"""
        # The summing re-orders things so it needs to be re-sorted
        if not self.results_data:
            _ = u.sort_by_value(u.sum_dict_values(self.results_by_index))
            self.results_data = dict(_)
        return self.results_data

    @property
    def indices(self):
        """Return all indices found"""
        if not self.indices_data:
            self.indices_data = list(self.usage_stats.keys())
        if len(self.indices_data) == 1:
            return self.indices_data[0]
        return self.indices_data

    def sum_index_stats(self, field_usage, idx):
        """Per field, sum all of the usage stats for all shards in ``idx``"""

        def appender(result, field, value):
            if field not in result:
                result[field] = value
            else:
                result[field] += value
            return result

        result = {}
        for shard in field_usage[idx]['shards']:
            for field in list(shard['stats']['fields'].keys()):
                if field in ['_id', '_source']:
                    # We don't care about these because these can be used by
                    # runtime queries
                    continue
                result = appender(result, field, shard['stats']['fields'][field]['any'])
        return result
