class Parser():
	"""
	Parser to parse out of different types of log files. Currently only
	used to parse from the nginx log format (from a csv) provided for
	the toy version of this project.
	"""
	def __init__(self, valid_fields: list[str]) -> None:
		self.valid_fields: set[str] = set(valid_fields)

	def parse_nginx_log_line(self, log_line: dict[str, str]) -> list[str, dict[str, str]]:
		try:
			http_verb, endpoint, http_version = log_line['request'].split(' ')
			section = endpoint.split('/')[1]

			# we're losing some granularity here since we're not adding the rest
			# (if any) of the endpoint into the metric name. i don't think this
			# is how i'd want to do this in a production environment because we
			# lose so much potential info, but i'm sticking to it here because
			# a) that's the most sophisticated level of granularity asked for by
			# the take home, and b) it means metric names are all at the same
			# level of granularity (useful for parsing/clustering/querying/etc).
			metric_name = f"{section}.{log_line['status']}"

			# copy and add our extra fields
			parsed_log_line = log_line.copy()
			parsed_log_line['http_verb'] = http_verb
			parsed_log_line['section'] = f"/{section}"
			parsed_log_line['endpoint'] = endpoint
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
