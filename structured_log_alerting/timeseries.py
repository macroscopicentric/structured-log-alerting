from abc import ABC, abstractmethod
from datetime import datetime, timedelta

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
	max_length : int, optional
		The max_length of the TimeSeries' data_points for individual
		data point storage. Defaults to 10.
	"""

	kind: None | str = None

	@abstractmethod
	def __init__(self, name: str, labels: dict, max_length: int = 10) -> None:
		self.name = name
		self.labels = labels

		self.data_points: SortedOrderedDict[datetime, int] = SortedOrderedDict(max_length)

	@abstractmethod
	def add_data_point(self, data_point) -> SortedOrderedDict:
		return self.data_points

class CounterSeries(TimeSeries):
	"""
	Non-abstract counter metric series class subclassed from the ABC TimeSeries.
	Counters here are monotonically increasing.

	See TimeSeries for attribute descriptions.
	"""

	kind = "counter"

	def __init__(self, name: str, labels: dict, max_length: int = 100) -> None:
		self.name = name
		self.max_length = max_length
		self.labels = labels
		self.data_points = SortedOrderedDict(max_length)

	def add_data_point(self, timestamp: datetime, count: int = 1) -> SortedOrderedDict:
		"""
		Add a data point to self.data_points

		Parameters
		----------
		timestamp : datetime
			The timestamp of the data point to add to the collection.
		count : int, optional
			The count to increment the data point by (defaults to 1).

		Returns
		-------
		SortedOrderedDict
			self.data_points
		"""
		if timestamp in self.data_points:
			self.data_points[timestamp] += count
		else:
			self.data_points[timestamp] = count

		return self.data_points

	def total_count_since(self, since_number_of_seconds: int, present_time: datetime = datetime.now()) -> int:
		"""
		Find the total count of events since the given timestamp.

		Parameters
		----------
		since_number_of_seconds : int
			The number of seconds into the past we should look for the
			count (exclusive of end of range).
		present_time : datetime
			The current time that should be considered the end bound
			(inclusive).

		Returns
		-------
		int
			The total count of events.
		"""
		now = present_time
		past_time = now - timedelta(seconds=since_number_of_seconds)

		count = 0

		# i think there's probably a neat way to do this with pandas
		# but i looked at the docs and haven't figured out what i might
		# need so we're punting on that for now.
		for key, value in self.data_points.items():
			if key > past_time and key <= now:
				count += value

		return count
