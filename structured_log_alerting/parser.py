from datetime import datetime
from typing import NamedTuple

class Request(NamedTuple):
	http_verb: str	
	endpoint: str
	section: str
	http_version: str

class Parser():
	"""
	Parser to parse out of different types of log files. Currently only
	used to parse from the nginx log format (from a csv) provided for
	the toy version of this project.
	"""
	def __init__(self, valid_fields: list[str]) -> None:
		self.valid_fields: set[str] = set(valid_fields)

	def parse_log_line(self, log_line: dict[str, str]) -> tuple[str, dict]:
		"""
		Parse an entire structured log line from a log file. This
		currently only works with log lines formatted as dictionaries,
		and expects a very specific set of fields. See example_log.csv
		in this project for a sample of the formatting and fields it
		expects.

		Parameters
		----------
		log_line : dict of str: str

		Returns
		-------
		str
			The dot-namespaced string of the metric name (to be used to
			decide which metric series to add the log line to).
		dict of str: str or datetime
			A modified dictionary of the original log line dictionary,
			with some additional fields added and the date reformatted.
		"""
		try:
			request: Request = self.parse_request(log_line)

			# we're losing some granularity here since we're not adding the rest
			# (if any) of the endpoint into the metric name. i don't think this
			# is how i'd want to do this in a production environment because we
			# lose so much potential info, but i'm sticking to it here because
			# a) that's the most sophisticated level of granularity asked for by
			# the take home, and b) it means metric names are all at the same
			# level of granularity (useful for parsing/clustering/querying/etc).
			metric_name = f"{request.section}.{log_line['status']}"

			# copy and add our extra fields
			parsed_log_line: dict = log_line.copy()
			parsed_log_line['date'] = self.parse_timestamp(log_line)
			parsed_log_line['http_verb'] = request.http_verb
			parsed_log_line['section'] = request.section
			parsed_log_line['endpoint'] = request.endpoint
			return metric_name, parsed_log_line

		# i could hold onto the malformed line and try to combine it with
		# line(s) below it in the file to build a single correct line.
		# but this is both easiest and i think a reasonable pattern
		# in metrics since some lossiness is okay (ie, i'm choosing
		# availabilty over consistency) and we cannot guarantee that
		# we'd end up with a properly formed line at the end of an
		# aggregation attempt. improperly formatted lines can manifest in a
		# variety of ways, and definitely in these two errors.
		except (AttributeError, ValueError) as e:
			print(f"Malformed log line, skipping: {log_line}") 
			raise ValueError

	def parse_request(self, log_line: dict[str, str]) -> Request:
		"""
		A helper method to parse the parts of the request field of a
		log line so we can use it in multiple places.

		Parameters
		----------
		log_line : dict of str: str
			The full log line.

		Returns
		-------
		Request	
			A named tuple of all the fields we currently want to parse
			out separately from the request field.
		"""
		http_verb, endpoint, http_version = log_line['request'].split(' ')
		section = endpoint.split('/')[1]
		request_elements: Request = Request(http_verb=http_verb, endpoint=endpoint, section=section, http_version=http_version)

		return request_elements

	def parse_timestamp(self, log_line: dict[str, str]) -> datetime | None:
		"""
		A helper method to parse out just the timestamp of a log line
		so we can use it in multiple places.

		Parameters
		----------
		log_line : dict of str: str
			The full log line.

		Returns
		-------
		datetime or None
			The timestamp, converted from UNIX epoch, or None (with a
			printed error) if the conversion was unsuccessful.
		"""
		try:
			timestamp = log_line['date']
			converted_to_datetime = datetime.fromtimestamp(int(timestamp))
			return converted_to_datetime

		# this does not feel like it lines up with the possible errors
		# listed in the docs for 3.11 but what do I know (I was able to
		# replicate these two specific errors via the python repl).
		# this will also catch a string timestamp that cannot be turned
		# into an int (which is a ValueError).
		except (OSError, ValueError) as e:
			print(f"Invalid timestamp, failed to parse: {timestamp}")
			return None
