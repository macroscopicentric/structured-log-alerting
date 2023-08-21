import pytest

from structured_log_alerting.sortedordereddict import SortedOrderedDict


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
        1549573865,
        1549573866,
        1549573867,
        1549573868,
    ]


def test_handles_adding_new_in_order_key(sample_unix_timestamps):
    test_dict = SortedOrderedDict(10)
    first_timestamp = sample_unix_timestamps[0]
    second_timestamp = sample_unix_timestamps[2]

    # We don't really care that all of these tests are overwriting keys
    # since that's how we'll be using this higher up anyway.
    for timestamp in sample_unix_timestamps[0:3]:
        test_dict[timestamp] = 1

    assert len(test_dict) == 2
    assert list(test_dict)[0] == first_timestamp
    assert list(test_dict)[-1] == second_timestamp


def test_handles_adding_new_out_of_order_key(sample_unix_timestamps):
    test_dict = SortedOrderedDict(10)
    first_timestamp = sample_unix_timestamps[0]
    second_timestamp = sample_unix_timestamps[2]
    third_timestamp = sample_unix_timestamps[5]

    for timestamp in sample_unix_timestamps[5:9]:
        test_dict[timestamp] = 1

    assert len(test_dict) == 3
    assert list(test_dict)[0] == first_timestamp
    assert list(test_dict)[1] == second_timestamp
    assert list(test_dict)[2] == third_timestamp


def test_deletes_past_max_len(sample_unix_timestamps):
    test_dict = SortedOrderedDict(3)

    for timestamp in sample_unix_timestamps:
        test_dict[timestamp] = 1

    assert len(test_dict) == 3
