from datetime import datetime
import pytest

from structured_log_alerting.timeseries import CounterSeries


@pytest.fixture
def sample_name():
    return "api.200"


@pytest.fixture
def sample_labels():
    return {
        "remotehost": "10.0.0.1",
        "verb": "GET",
        "endpoint": "/api/user",
        "section": "/api",
        "status": 200,
    }


@pytest.fixture
def sample_timestamps():
    return [
        datetime(2019, 2, 7, 16, 11, 3),
        datetime(2019, 2, 7, 16, 11, 3),
        datetime(2019, 2, 7, 16, 11, 4),
        datetime(2019, 2, 7, 16, 11, 4),
        datetime(2019, 2, 7, 16, 11, 4),
        datetime(2019, 2, 7, 16, 11, 5),
        datetime(2019, 2, 7, 16, 11, 5),
        datetime(2019, 2, 7, 16, 11, 4),
        datetime(2019, 2, 7, 16, 11, 3),
        datetime(2019, 2, 7, 16, 11, 5),
    ]


def test_counter_initializes_correctly(sample_name, sample_labels):
    counter = CounterSeries(sample_name, sample_labels)

    assert counter.kind == "counter"
    assert counter.name == sample_name
    assert counter.labels == sample_labels
    assert len(counter.data_points) == 0


def test_counter_handles_first_timestamp_insertion(
    sample_name, sample_labels, sample_timestamps
):
    counter = CounterSeries(sample_name, sample_labels)
    counter.add_data_point(sample_timestamps[0])

    assert len(counter.data_points) == 1
    timestamp, count = counter.data_points.popitem()
    assert count == 1


def test_counter_handles_incrementing_existing_timestamp(
    sample_name, sample_labels, sample_timestamps
):
    first_unix_timestamp = sample_timestamps[0]
    counter = CounterSeries(sample_name, sample_labels)
    counter.add_data_point(first_unix_timestamp)
    counter.add_data_point(first_unix_timestamp)

    assert len(counter.data_points) == 1
    timestamp, count = counter.data_points.popitem()
    assert count == 2


def test_counter_returns_count_since_time(
    sample_name, sample_labels, sample_timestamps
):
    counter = CounterSeries(sample_name, sample_labels)
    current_time = datetime(2019, 2, 7, 16, 11, 6)
    for timestamp in sample_timestamps:
        counter.add_data_point(timestamp)

    count = counter.total_count_since(current_time, 10)

    assert count == len(sample_timestamps)
