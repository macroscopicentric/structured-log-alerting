import pytest

from structured_log_alerting.alertmanager import AlertManager
from structured_log_alerting.metricscollection import CountersCollection

@pytest.fixture
def counters_collection(api_200_metric_name, api_200_parsed_log, api_200_newer_parsed_log, report_200_metric_name, report_200_parsed_log, report_404_metric_name, report_404_parsed_log):
	counters_collection = CountersCollection()

	counters_collection.add_or_update_series(api_200_metric_name, api_200_parsed_log)	
	counters_collection.add_or_update_series(api_200_metric_name, api_200_newer_parsed_log)	
	counters_collection.add_or_update_series(report_200_metric_name, report_200_parsed_log)	
	counters_collection.add_or_update_series(report_404_metric_name, report_404_parsed_log)	

	return counters_collection

@pytest.fixture
def most_recent_time(api_200_newer_parsed_log):
	return api_200_newer_parsed_log['date']

def test_alertmanager_summarizes_interesting_counters(counters_collection, most_recent_time):
	interesting_counters = ['404', '500']
	alertmanager = AlertManager(counters_collection, interesting_counters)
	summary = alertmanager.find_interesting_metrics_summaries(most_recent_time)

	assert type(summary) == list
	assert len(summary) == 2
	assert '404' in summary[0]
	assert ' 1 ' in summary[0]

def test_alertmanager_summarizes_manually_added_interesting_counters(counters_collection, most_recent_time):
	metrics_to_summarize = ['api']
	alertmanager = AlertManager(counters_collection)
	summary = alertmanager.find_interesting_metrics_summaries(most_recent_time, 10, metrics_to_summarize)

	assert type(summary) == list
	assert len(summary) == 1
	assert 'api' in summary[0]
	assert ' 2 ' in summary[0]

def test_alertmanager_interesting_counters_prints_error_if_neither_is_given(counters_collection, most_recent_time):
	metrics_to_summarize = []
	alertmanager = AlertManager(counters_collection)
	summary = alertmanager.find_interesting_metrics_summaries(most_recent_time)

	assert type(summary) == list
	assert len(summary) == 1
	assert 'Error' in summary[0]

def test_alertmanager_gives_highest_count_with_manually_added_metrics(counters_collection, most_recent_time):
	metrics_to_count = ['404', '500']
	alertmanager = AlertManager(counters_collection)
	highest_count_summary = alertmanager.find_highest_count(most_recent_time, 10, metrics_to_count)

	assert type(highest_count_summary) == str
	assert '404' in highest_count_summary
	assert '(1)' in highest_count_summary

def test_alertmanager_gives_highest_count_with_sections_by_default(counters_collection, most_recent_time):
	alertmanager = AlertManager(counters_collection)
	highest_count_summary = alertmanager.find_highest_count(most_recent_time)

	assert type(highest_count_summary) == str
	assert 'api' in highest_count_summary
	assert '(2)' in highest_count_summary
