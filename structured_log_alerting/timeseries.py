from abc import ABC, abstractmethod
from collections import deque, OrderedDict
from datetime import datetime

class TimeSeries(ABC):
	"""
	Abstract base class for a single metric series, should be subclassed
	based on metric type (ex: counter, histogram).

	Attributes
	----------
	name : str
		The short name of the metric.

	max_length : int
		The maximum length of the data points iterable.
		self.data_points will occasionally go above max_length
		(see #truncate_if_needed below).

	labels : dict of str: str
		A dictionary of key/value label pairs to be used to aggregate metrics.
	"""

	kind: None | str = None

	@abstractmethod
	def __init__(self, name: str, labels: dict, max_length: int = 10):
		self.name = name
		self.max_length = max_length
		self.labels = labels

		self.data_points: dict[datetime, int] = OrderedDict()

	@abstractmethod
	def add_data_point(self, data_point):
		self.__truncate_if_needed()
		return self.data_points

	def _truncate_if_needed(self):
		"""
		A helper method to determine if our data points dictionary has
		gone over our manually defined max_length.

		Notes
		-----
		There are generally two philosophies about when to perform an action
		like this, which I'll call limits or requests (a la k8s). Ie, you
		can either choose to never go over a limit by preemptively
		removing elements every time you add elements, or you can just
		retroactively check the length and then pare down if you've gone
		over. In a product environment I'd probably choose the former,
		especially in a domain like metrics where memory and disk usage
		tend to be tightly controlled (and often fixed size). But this is
		easier, this is very much a "good enough" solution here.
		"""
		while len(self.data_points) > self.max_length:
			self.data_points.popitem(False)

		return self.data_points

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
		self.data_points = OrderedDict()

	def add_data_point(self, timestamp: int, count: int = 1):
		try:
			converted_to_datetime = datetime.fromtimestamp(timestamp)
			if converted_to_datetime in self.data_points:
				self.data_points[converted_to_datetime] += 1
			else:
				self._insert(converted_to_datetime)
				# possibly need to re-sort keys before insertion
			self._truncate_if_needed()
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

	def _insert(self, timestamp: datetime):
		"""
		This is a helper method to insert, and possibly re-sort, the data
		points iterable. At the end of this method, all data points should
		be stored in chronological order.

		Notes
		-----
		Under normal production conditions I might be happy with (logging
		and then) throwing out out-of-order timestamps, but the number in
		the sample data here is fairly extreme (about one in five after a
		brief look), so I'm assuming I'm supposed to handle them instead.
		"""
		stashed_counters: deque[tuple[datetime, int]] = deque()
		if len(self.data_points) > 0:
			while len(self.data_points) and list(self.data_points)[-1] > timestamp:
				data_point = self.data_points.popitem()
				stashed_counters.appendleft(data_point)

		self.data_points[timestamp] = 1

		# If I could guarantee timestamps would only be one second off
		# I could just use OrderedDict's built-in #move_to_end method
		# instead of having this extra stashed_counters deque but
		# having looked at the data I know I can't.
		self.data_points.update(stashed_counters)

		return self.data_points
