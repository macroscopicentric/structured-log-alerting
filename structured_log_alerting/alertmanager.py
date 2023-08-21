from datetime import datetime

from structured_log_alerting.metricscollection import CountersCollection


class AlertManager:
    """
    Tracks if and when we should alert on anything. This is currently
    used for two types of alerts: unconditional 10s summaries, and
    conditional 2min request totals in the case of elevated requests.

    Attributes
    ----------
    counters_collection : CountersCollection
            the full counter metrics to track and summarize
    elevated_request_threshold : int, optional
            At what number of requests (averaged) should AM start alerting.
            Defaults to 10.
    interesting_counters : list of str, optional
            Substrings or full names of counters to track and report on
            when summarizing recent request patterns.

    Notes
    -----
    Although I've never looked at it intensively, Prometheus' Alert
    Manager (which this name is obviously based on, and which also has
    an additional separate layer I've skipped here called the Rule
    Manager) is a separate project that can be installed separately
    from Prometheus. I suspect this means it uses more of a client-
    broker model where Prometheus simply sends rule matches to Alert
    Manager as messages and they go into a queue to be handled. I think
    that model makes a lot of sense for several reasons, but a big one
    is that those two tasks are both pretty resource-intensive but rule
    aggregation and log storage will always take significantly more
    work, and the two streams can also be parallelized. In a toy
    program like this, however, that would take threads or something
    else and I don't know how to do that. So we're leaving this as a
    much simpler version where we just pass in the CountersCollection
    and the AlertManager instance simply handles the entire thing.
    """

    def __init__(
        self,
        counters_collection: CountersCollection,
        interesting_counter_names: list[str] = [],
        elevated_request_threshold: int = 10,
    ) -> None:
        self.counters_collection = counters_collection
        self.interesting_counters = interesting_counter_names
        self.elevated_request_threshold = elevated_request_threshold

    def find_highest_count(
        self,
        current_time: datetime = datetime.now(),
        since_interval_in_seconds: int = 10,
        metric_names: list[str] = [],
    ) -> str:
        """
        Find and record a summary statement for a type of metric with
        the most requests within a specific time interval.

        Parameters
        ----------
        current_time : datetime, optional
                The timestamp we should treat as the present. Defaults to
                datetime.now()
        since_interval_in_seconds : int, optional
                The interval in seconds (exclusive of the left end, inclusive
                of the right end) to provide a summary for. Defaults to 10.
        metric_names : list of str, optional
                The list of strings with which to query metric names.
                Optional, defaults to an empty list, which will the attached
                CountersCollections' list of top-level API sections.

        Returns
        -------
        str
                A single-line summary of the highest count metric and its count.
        """
        metric_names_to_check: list[str] = []
        metric_type: str = "metric"

        if len(metric_names) > 0:
            metric_names_to_check = metric_names
        else:
            metric_names_to_check = self.counters_collection.sections
            metric_type = "section"

        most_requested_metric: str = ""
        most_requested_counter: int = 0
        for metric in metric_names_to_check:
            temp_count: int = self.counters_collection.total_count_since(
                current_time, since_interval_in_seconds, metric
            )
            if temp_count > most_requested_counter:
                most_requested_metric = metric
                most_requested_counter = temp_count

        highest_count_summary: str = f"The {metric_type} with the most requests ({most_requested_counter}) in the last ten seconds was: {most_requested_metric}"

        return highest_count_summary

    def find_interesting_metrics_summaries(
        self,
        current_time: datetime = datetime.now(),
        since_interval_in_seconds: int = 10,
        metric_names: list[str] = [],
    ) -> list[str]:
        """
        Given a specific interval of time, provide sentence-length
        summaries of some metrics, either passed in, or the instance's
        own list of "interesting counters" (provided on initialization).

        Parameters
        ----------
        current_time : datetime, optional
                The timestamp we should treat as the present. Defaults to
                datetime.now()
        since_interval_in_seconds : int, optional
                The interval in seconds (exclusive of the left end, inclusive
                of the right end) to provide a summary for. Defaults to 10.
        metric_names : list of str, optional
                The list of strings with which to query metric names.
                Optional, defaults to an empty list, which will use
                self.interesting_counters.

        Returns
        -------
        list of str
                The collection of sentences about the summarized output, to
                be printed by the main body of the program.
        """
        try:
            summary_statements: list[str] = []
            metric_names_to_check: list[str] = []

            if len(metric_names) > 0:
                metric_names_to_check = metric_names
            elif len(self.interesting_counters) > 0:
                metric_names_to_check = self.interesting_counters
            else:
                # i think ideally this would be a custom type of error
                # we'd raise here and then catch, but we'll just use
                # ValueError (closest possible) to catch this. basically,
                # both self.interesting_counters and the metric_names
                # param here are optional but you must have _one_ of
                # them to define what kinds of metrics we want to look
                # at for the summary. raise if you don't have either.
                raise ValueError

            # summarize interesting metrics
            for metric in metric_names_to_check:
                count = self.counters_collection.total_count_since(
                    current_time, since_interval_in_seconds, metric
                )
                summary_statements.append(
                    f"There have been {count} counts of a {metric} in the last {since_interval_in_seconds} seconds."
                )

        except ValueError as e:
            summary_statements.append(
                """
				Error: No metric_names passed in and no interesting_counters used
				when initializing this instance of AlertManager. You will not
				receive any summary details because I don't know what to summarize.
				Please set up one of the two in main.py and then re-run the program.
				"""
            )

        return summary_statements

    def provide_summary_for_interval(
        self,
        current_time: datetime = datetime.now(),
        since_interval_in_seconds: int = 10,
        interesting_metrics: list[str] = [],
        metrics_for_highest_count: list[str] = [],
    ) -> list[str]:
        """
        Given a specific interval of time, provide sentence-length
        summaries of some metrics. This currently returns a collection
        of summary statements describing the most-requested metric
        and any other interesting metrics.

        Parameters
        ----------
        current_time : datetime, optional
                The timestamp we should treat as the present. Defaults to
                datetime.now()
        since_interval_in_seconds : int, optional
                The interval in seconds (exclusive of the left end, inclusive
                of the right end) to provide a summary for. Defaults to 10.
        interesting_metrics : list of str, optional
                The list of strings with which to query metric names for
                total count of "interesting" metric events.
                Optional, defaults to an empty list, which will use
                self.interesting_counters.
        metrics_for_highest_count : list of str, optional
                The list of strings to check for the collection with the
                highest count in the last time interval. Optional, defaults
                to an empty list, which will use self.counters_collection.sections

        Returns
        -------
        list of str
                The collection of sentences about the summarized output, to
                be printed by the main body of the program.
        """
        summary_statements: list[str] = []

        formatted_timestamp_for_printing = current_time.isoformat(" ", "seconds")
        summary_statements.append(
            f"Current time interval: {formatted_timestamp_for_printing}"
        )

        summary_statements.append(
            self.find_highest_count(
                current_time, since_interval_in_seconds, metrics_for_highest_count
            )
        )
        summary_statements.extend(
            self.find_interesting_metrics_summaries(
                current_time, since_interval_in_seconds, interesting_metrics
            )
        )

        return summary_statements

    def check_for_elevated_requests(
        self, since_interval_in_seconds: int = 120
    ) -> list[str]:
        """
        Check across all request counter metrics whether average
        requests has been elevated above the instance's request
        threshold.

        Parameters
        ----------
        since_interval_in_seconds : int, optional
                The interval in seconds (exclusive of the left end, inclusive
                of the right end) to provide a summary for. Defaults to 10.

        Returns
        -------
        list of str
                The collection of sentences about the summarized output, to
                be printed by the main body of the program.
        """
        pass
