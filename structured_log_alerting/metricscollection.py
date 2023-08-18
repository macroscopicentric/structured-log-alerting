from datetime import datetime

from structured_log_alerting.timeseries import CounterSeries

class MetricsCollection():
	"""
	Keep track of all metrics series, which allows queries and
	aggregations across multiple/all series.

	Notes
	-----
	This is, for all intents and purposes, the equivalent to a(n
	in-memory) TSDB in this project. This is deliberately not an
	Abstract Base Class because we should be able to collect and track
	all kinds of metrics together, but will not be used in this toy
	project as-is because we currently only have counters.
	"""
	def __init__(self) -> None:
		self.sections: set[str] = set()
		self.counters_collection = CountersCollection()

class CountersCollection(MetricsCollection):
	"""
	A collection of all counters specifically, so we can do counter-
	specific aggregations and queries (ex: summations) that wouldn't
	necessarily make sense for other types of metrics.
	"""
	def __init__(self) -> None:
		self.sections = set()
		self.series: dict[str, CounterSeries] = {}

	def _add_series(self, counter_name: str, parsed_log_file: dict) -> dict[str, CounterSeries]:
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
		valid_labels: list[str] = ['remotehost', 'section', 'endpoint', 'http_verb', 'status']
		labels: dict[str, str] = {}

		for label in valid_labels:
			labels[label] = parsed_log_file[label]

		new_counter = CounterSeries(counter_name, labels)
		self.series[counter_name] = new_counter
		if parsed_log_file['section'] not in self.sections:
			self.sections.add(parsed_log_file['section'])

		return self.series

	def add_or_update_series(self, counter_name: str, parsed_log_file: dict) -> dict[str, CounterSeries]:
		"""
		Finds and updates or creates the appropriate counter series
		and adds the new log file information as a new metric.
		"""
		if counter_name not in self.series:
			self._add_series(counter_name, parsed_log_file)

		timestamp = parsed_log_file['date']
		self.series[counter_name].add_data_point(timestamp)

		return self.series

	def total_count_since(self, metrics_namespace: str, since: datetime, until: datetime = datetime.now()) -> int:
		"""
		Find all counter series matching a specific metric namespace
		since a specific time.

		Parameters
		----------
		metrics_namespace : str
			The parent namespace in which to find all metrics.
		since : datetime
			The timestamp (inclusive) to use as the lower bound when querying
		until : datetime
			The timestamp (inclusive) to use as the upper bound when querying

		Returns
		-------
		int
			The total count of events.
		"""
		pass
