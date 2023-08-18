from datetime import datetime
import pytest

from structured_log_alerting.timeseries import CounterSeries

@pytest.fixture
def sample_name():
	return 'api.200'

@pytest.fixture
def sample_labels():
	return {
		'remotehost': "10.0.0.1",
		'verb': 'GET',
		'endpoint': '/api/user',
		'section': '/api',	
		'status': 200
	}

@pytest.fixture
def sample_unix_timestamps():
	return [
		1549573863,
		1549573863,
		1549573864,
		1549573864,
		1549573864,
		1549573865,
		1549573865,
		1549573864,
		1549573863,
		1549573865	
	]

def test_counter_initializes_correctly(sample_name, sample_labels):
	counter = CounterSeries(sample_name, sample_labels)

	assert counter.kind == 'counter'
	assert counter.name == sample_name
	assert counter.labels == sample_labels
	assert len(counter.data_points) == 0

def test_too_long_timestamp_handles_oserror(capsys, sample_name, sample_labels):
	invalid_timestamp = 1111111111111111111
	counter = CounterSeries(sample_name, sample_labels)
	counter.add_data_point(invalid_timestamp)
	out, err = capsys.readouterr()

	assert out == f"Invalid timestamp, failed to add data point: {invalid_timestamp}\n"
	assert len(counter.data_points) == 0

def test_invalid_timestamp_handles_valueerror(capsys, sample_name, sample_labels):
	invalid_timestamp = 33333333333333333
	counter = CounterSeries(sample_name, sample_labels)
	counter.add_data_point(invalid_timestamp)
	out, err = capsys.readouterr()

	assert out == f"Invalid timestamp, failed to add data point: {invalid_timestamp}\n"
	assert len(counter.data_points) == 0

def test_counter_handles_first_timestamp_insertion(sample_name, sample_labels, sample_unix_timestamps):
	counter = CounterSeries(sample_name, sample_labels)
	counter.add_data_point(sample_unix_timestamps[0])

	assert len(counter.data_points) == 1
	timestamp, count = counter.data_points.popitem()
	assert count == 1

def test_counter_handles_incrementing_existing_timestamp(sample_name, sample_labels, sample_unix_timestamps):
	first_unix_timestamp = sample_unix_timestamps[0]
	counter = CounterSeries(sample_name, sample_labels)	
	counter.add_data_point(first_unix_timestamp)
	counter.add_data_point(first_unix_timestamp)

	assert len(counter.data_points) == 1
	timestamp, count = counter.data_points.popitem()
	assert count == 2
