import argparse
import csv

from structured_log_alerting.metricscollection import CountersCollection

def parse_log_line(log_line: dict[str, str]):
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
		parsed_log_line = log_line.copy()
		parsed_log_line['http_verb'] = http_verb
		parsed_log_line['section'] = f"/{section}"
		parsed_log_line['endpoint'] = endpoint
		# print(metric_name)
		# print(parsed_log_line)
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
		return None, None

def main():
	# argparse stuff
	parser = argparse.ArgumentParser()
	parser.add_argument("file_location", help="the location of the csv-formatted log file", type=str)
	args = parser.parse_args()

	counters_collection = CountersCollection()

	# ideally i'd like to separate the io out of main for a bunch of
	# reasons (readable code, testability) but only opening the file
	# once gets me the perks of an iterable (specifically, the combo
	# of line buffering + line tracking with the power of #__next__())
	# and i'm not sure how to get that without basically reimplementing
	# this as a class that manually reinvents all of that.
	with open(args.file_location) as f:
		reader = csv.DictReader(f)
		number_of_fields = len(reader.fieldnames)
		for line in reader:
			# print(reader.line_num)
			metric_name, parsed_log_line = parse_log_line(line)
			if metric_name != None:
				counters_collection.add_or_update_series(metric_name, parsed_log_line)
				# print(f"metric: {metric_name}")
				# print(counters_collection.counter_series[metric_name].data_points)

if __name__ == "__main__":
	main()
