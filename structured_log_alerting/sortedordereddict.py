from collections import deque, OrderedDict

class SortedOrderedDict(OrderedDict):
	"""
	This is a regular OrderedDict with two important changes:
	1. Elements will remain sorted in ascending order by default.
	2. There's a size limit on how large the dict can grow, similar to
		how a deque works.

	Attributes
	----------
	max_len : int
		The maximum length the SortedOrderedDict may grow to (measured
		like a regular dict in keys and not full size).
	"""
	def __init__(self, max_len: int,  /, *args, **kwargs) -> None:
		# TODO: it might be nice if this class supported descending
		# order as an alternative, but I don't need it for this work
		# so I'm going to skip implementing it for now.
		self.max_len = max_len
		super().__init__(*args, **kwargs)

	def __setitem__(self, key, value) -> None:
		"""
		Override default __setitem__ to ensure all new keys get added
		in ascending order and that the dict respects max_length at the
		end of this action.

		Notes
		-----
		Under different circumstances I might be able to handle this
		(either here or further up the chain) using OrderedDict's
		regular method #move_to_end, but unfortunately given the sample
		data we cannot guarantee that keys will only arrive in
		off-by-one out-of-order sequence.
		"""
		out_of_order_kv_pairs: deque[tuple] = deque()

		if len(self) > 0:
			while len(self) and list(self)[-1] > key:
				key_value_pair = self.popitem()
				out_of_order_kv_pairs.appendleft(key_value_pair)

		super().__setitem__(key, value)
		self.update(out_of_order_kv_pairs)

		if len(self) > self.max_len:
			self.popitem(False)
