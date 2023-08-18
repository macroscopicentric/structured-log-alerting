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

		self.data_points: dict[datetime, int] = SortedOrderedDict(max_length)

	@abstractmethod
	def add_data_point(self, data_point):
		pass

class CounterSeries(TimeSeries):
	"""
	Non-abstract counter metric series class subclassed from the ABC TimeSeries.
	Counters here are non-monotonic.

	See TimeSeries for attribute descriptions.
	"""

	kind = "counter"

	def __init__(self, name: str, labels: dict, max_length: int = 10):
		self.name = name
		self.max_length = max_length
		self.labels = labels
		self.data_points = SortedOrderedDict(max_length)

	def add_data_point(self, timestamp: int, count: int = 1):
		try:
			converted_to_datetime = datetime.fromtimestamp(timestamp)
			if converted_to_datetime in self.data_points:
				self.data_points[converted_to_datetime] += 1
			else:
				self.data_points[converted_to_datetime] = 1

		# this does not feel like it lines up with the possible errors
		# listed in the docs for 3.11 but what do I know (I was able to
		# replicate these two specific errors via the python repl).
		except (OSError, ValueError) as e:
			print(f"Invalid timestamp, failed to add data point: {timestamp}")

		return self.data_points

	def total_count_since(self, timestamp: datetime):
		"""
		Find the total count of events since the given timestamp.

		Parameters
		----------
		timestamp : datetime
			The earliest bound (inclusive) of event timestamps.

		Returns
		-------
		int
			The total count of events.
		"""
		pass
