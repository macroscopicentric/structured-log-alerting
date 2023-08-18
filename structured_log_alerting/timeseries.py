from abc import ABC, abstractmethod
from datetime import datetime

from structured_log_alerting.sortedordereddict import SortedOrderedDict

class TimeSeries(ABC):
	"""
	Abstract base class for a single metric series, should be subclassed
	based on metric type (ex: counter, histogram).

	Attributes
	----------
	name : str
		The short name of the metric.

	labels : dict of str: str
		A dictionary of key/value label pairs to be used to aggregate metrics.
	"""

	kind: None | str = None

	@abstractmethod
	def __init__(self, name: str, labels: dict, max_length: int = 10):
		self.name = name
		self.labels = labels

		self.data_points: SortedOrderedDict[datetime, int] = SortedOrderedDict(max_length)

	@abstractmethod
	def add_data_point(self, data_point) -> SortedOrderedDict:
		return self.data_points

class CounterSeries(TimeSeries):
	"""
	Non-abstract counter metric series class subclassed from the ABC TimeSeries.
	Counters here are non-monotonic.

	See TimeSeries for attribute descriptions.
	"""

	kind = "counter"

	def __init__(self, name: str, labels: dict, max_length: int = 100) -> None:
		self.name = name
		self.max_length = max_length
		self.labels = labels
		self.data_points = SortedOrderedDict(max_length)

	def add_data_point(self, timestamp: str, count: int = 1) -> SortedOrderedDict:
		try:
			converted_to_datetime = datetime.fromtimestamp(int(timestamp))
			if converted_to_datetime in self.data_points:
				self.data_points[converted_to_datetime] += 1
			else:
				self.data_points[converted_to_datetime] = 1

		# this does not feel like it lines up with the possible errors
		# listed in the docs for 3.11 but what do I know (I was able to
		# replicate these two specific errors via the python repl).
		# this will also catch a string timestamp that cannot be turned
		# into an int (which is a ValueError).
		except (OSError, ValueError) as e:
			print(f"Invalid timestamp, failed to add data point: {timestamp}")

		return self.data_points

	def total_count_since(self, since: datetime, until: datetime = datetime.now()) -> int:
		"""
		Find the total count of events since the given timestamp.

		Parameters
		----------
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
