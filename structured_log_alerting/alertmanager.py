class AlertManager():
	"""
	Tracks if and when we should alert on anything. This is currently
	used for two types of alerts: unconditional 10s summaries, and
	conditional 2min request totals in the case of elevated requests.

	Attributes
	----------
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
	def __init__(self, elevated_request_threshold: int = 10, interesting_counter_names: list[str] = []) -> None:
		self.elevated_request_threshold = elevated_request_threshold
		self.interesting_counters = interesting_counter_names

	def provide_summary_for_interval(self, interval_in_seconds: int = 10, metric_names: list[str] = []) -> list[str]:
		"""
		Given a specific interval of time, provide sentence-length
		summaries of some metrics, either passed in, or the instance's
		own list of "interesting counters" (provided on initialization).

		Parameters
		----------
		interval_in_seconds : int, optional
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
		pass

	def check_for_elevated_requests(self, interval_in_seconds: int = 120) -> list[str]:
		"""
		Check across all request counter metrics whether average
		requests has been elevated above the instance's request
		threshold.

		Parameters
		----------
		interval_in_seconds : int, optional
			The interval in seconds (exclusive of the left end, inclusive
			of the right end) to provide a summary for. Defaults to 10.

		Returns
		-------
		list of str
			The collection of sentences about the summarized output, to
			be printed by the main body of the program.
		"""