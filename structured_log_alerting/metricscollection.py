from abc import ABC, abstractmethod
from datetime import datetime

from structured_log_alerting.timeseries import CounterSeries


class MetricsCollection(ABC):
    """
    Generic metrics collection class, used to subclass specific types of metrics.

    Attributes
    ----------
    max_series_length : int
        The allowed upper length on each individual series stored in this
        collection.
    sections : list of str
        The main API sections being tracked with metrics.

    Notes
    -----
    Like TimeSeries and CounterSeries, we won't use MetricsCollection for anything
    more than a parent ABC for our counters collection. But in theory this would be
    extendable if we did end up with other kinds of metrics.
    """

    @abstractmethod
    def __init__(self, max_series_length: int = 100) -> None:
        self.max_series_length = max_series_length
        self.sections: list[str] = []


class CountersCollection(MetricsCollection):
    """
    A collection of all counters specifically, so we can do counter-
    specific aggregations and queries (ex: summations) that wouldn't
    necessarily make sense for other types of metrics.
    """

    def __init__(self, max_series_length: int = 100) -> None:
        super().__init__(max_series_length)
        self.series: dict[str, CounterSeries] = {}

    def _add_series(
        self, counter_name: str, parsed_log_file: dict
    ) -> dict[str, CounterSeries]:
        """
        Adds a new counter series to the instance's series
        dictionary. Does not check for whether the series previously
        existed, which makes it possible to accidentally overwrite
        entire series. Use #add_or_update_series as your entry
        point into this class to avoid doing so.
        """
        # cherry-pick the labels we care about from the log file
        # this should be put somewhere else, probably ideally some
        # sort of parsed log class so we can grab via attr rather
        # than hardcoding these strings everywhere.
        valid_labels: list[str] = [
            "remotehost",
            "section",
            "endpoint",
            "http_verb",
            "status",
        ]
        labels: dict[str, str] = {}

        for label in valid_labels:
            labels[label] = parsed_log_file[label]

        new_counter = CounterSeries(counter_name, labels, self.max_series_length)
        self.series[counter_name] = new_counter
        if parsed_log_file["section"] not in self.sections:
            self.sections.append(parsed_log_file["section"])

        return self.series

    def add_or_update_series(
        self, counter_name: str, parsed_log_file: dict
    ) -> dict[str, CounterSeries]:
        """
        Finds and updates or creates the appropriate counter series
        and adds the new log file information as a new metric.

        Parameters
        ----------
        counter_name : str
                The counter series to find or add.
        parsed_log_file : dict
                The pre-parsed log file as a dictionary.

        Returns
        -------
        dict of str, CounterSeries
                self.series
        """
        if counter_name not in self.series:
            self._add_series(counter_name, parsed_log_file)

        self.series[counter_name].add_data_point(parsed_log_file["date"])

        return self.series

    def total_count_since(
        self,
        current_time: datetime = datetime.now(),
        since_number_of_seconds: int = 10,
        metrics_namespace: str = "",
    ) -> int:
        """
        Find all counter series matching a specific metric namespace
        since a specific time.

        Parameters
        ----------
        current_time : datetime, optional
                The timestamp (inclusive) to use as the upper bound when
                querying. Defaults to the internal clock's datetime.now()
                when left out.
        since_number_of_seconds : int, optional
                The number of seconds (exclusive) to use as the lower bound
                when querying. Defaults to 10.
        metrics_namespace : str, optional
                The parent namespace in which to find all metrics. Defaults
                to all metrics when left out.

        Returns
        -------
        int
                The total count of events.
        """
        count = 0
        for series_name, series in self.series.items():
            if series_name.find(metrics_namespace) >= 0:
                count += series.total_count_since(current_time, since_number_of_seconds)

        return count
