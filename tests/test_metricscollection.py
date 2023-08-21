from datetime import datetime
import pytest

from structured_log_alerting.metricscollection import CountersCollection

@pytest.fixture
def api_200_metric_name():
	return 'api.200'

@pytest.fixture
def api_200_parsed_log():
	return {
		'remotehost': '10.0.0.1',
		'rfc931': '-',
		'authuser': 'apache',
		'date': datetime(2019, 2, 7, 16, 18, 58),
		'request': 'POST /api/user HTTP/1.0',
		'status': '200',
		'bytes': '1307',
		'http_verb': 'POST',
		'section': '/api',
		'endpoint': '/api/user'
	}

@pytest.fixture
def api_200_newer_parsed_log():
	return {
		'remotehost': '10.0.0.1',
		'rfc931': '-',
		'authuser': 'apache',
		'date': datetime(2019, 2, 7, 16, 18, 59),
		'request': 'POST /api/user HTTP/1.0',
		'status': '200',
		'bytes': '1307',
		'http_verb': 'POST',
		'section': '/api',
		'endpoint': '/api/user'
	}

@pytest.fixture
def report_200_metric_name():
	return 'report.200'

@pytest.fixture
def report_200_parsed_log():
	return {
		'remotehost': '10.0.0.1',
		'rfc931': '-',
		'authuser': 'apache',
		'date': datetime(2019, 2, 7, 16, 18, 58),
		'request': 'POST /report HTTP/1.0',
		'status': '200',
		'bytes': '1307',
		'http_verb': 'POST',
		'section': '/report',
		'endpoint': '/report'
	}

def test_counters_collection_adds_new_series(api_200_metric_name, api_200_parsed_log):
	counters_collection = CountersCollection()
	counters_collection.add_or_update_series(api_200_metric_name, api_200_parsed_log)

	assert len(counters_collection.series) == 1
	assert api_200_metric_name in counters_collection.series

def test_counters_collection_updates_existing_series(api_200_metric_name, api_200_parsed_log):
	counters_collection = CountersCollection()
	counters_collection.add_or_update_series(api_200_metric_name, api_200_parsed_log)
	counters_collection.add_or_update_series(api_200_metric_name, api_200_parsed_log)

	timestamp = api_200_parsed_log['date']

	assert len(counters_collection.series) == 1
	# this one's a little reachy but this is the most top-level thing
	# that would actually change on update
	assert counters_collection.series[api_200_metric_name].data_points[timestamp] == 2

def test_counters_colletion_tracks_sections(api_200_metric_name, api_200_parsed_log, report_200_metric_name, report_200_parsed_log):
	counters_collection = CountersCollection()
	counters_collection.add_or_update_series(api_200_metric_name, api_200_parsed_log)
	counters_collection.add_or_update_series(report_200_metric_name, report_200_parsed_log)

	assert len(counters_collection.sections) == 2
	assert api_200_parsed_log['section'] in counters_collection.sections
	assert report_200_parsed_log['section'] in counters_collection.sections

def test_counters_collection_collects_all_metrics_since_time(api_200_metric_name, api_200_parsed_log, report_200_metric_name, report_200_parsed_log):
	counters_collection = CountersCollection()
	counters_collection.add_or_update_series(api_200_metric_name, api_200_parsed_log)
	counters_collection.add_or_update_series(report_200_metric_name, report_200_parsed_log)
	count = counters_collection.total_count_since(datetime(2019, 2, 7, 16, 18, 59), 5)

	assert count == 2

def test_counters_collection_total_since_time_respects_metric_name_filtering(api_200_metric_name, api_200_parsed_log, report_200_metric_name, report_200_parsed_log):
	counters_collection = CountersCollection()
	counters_collection.add_or_update_series(api_200_metric_name, api_200_parsed_log)
	counters_collection.add_or_update_series(report_200_metric_name, report_200_parsed_log)
	count = counters_collection.total_count_since(datetime(2019, 2, 7, 16, 18, 59), 5, 'api')

	assert count == 1

def test_counters_collection_total_since_time_respects_exclusive_lower_bound(api_200_metric_name, api_200_parsed_log, api_200_newer_parsed_log):
	counters_collection = CountersCollection()
	counters_collection.add_or_update_series(api_200_metric_name, api_200_parsed_log)
	counters_collection.add_or_update_series(api_200_metric_name, api_200_newer_parsed_log)
	count = counters_collection.total_count_since(datetime(2019, 2, 7, 16, 18, 59), 1)

	assert count == 1
