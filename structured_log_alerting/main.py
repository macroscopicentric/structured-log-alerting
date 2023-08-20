import argparse
import csv
from datetime import datetime

from structured_log_alerting.metricscollection import CountersCollection
from structured_log_alerting.parser import Parser

def main():
	# argparse stuff
	parser = argparse.ArgumentParser()
	parser.add_argument("file_location", help="the location of the csv-formatted log file", type=str)
	args = parser.parse_args()

	# ideally i'd like to separate the io out of main for a bunch of
	# reasons (readable code, testability) but only opening the file
	# once gets me the perks of an iterable (specifically, the combo
	# of line buffering + line tracking with the power of #__next__())
	# and i'm not sure how to get that without basically reimplementing
	# this as a class that manually reinvents all of that.
	with open(args.file_location) as f:
		reader = csv.DictReader(f)

		counters_collection = CountersCollection()
		parser = Parser(reader.fieldnames)
		current_time = datetime.min

		for line in reader:
			try:
				metric_name, parsed_log_line = parser.parse_log_line(line)
				# print(metric_name)
				# print(parsed_log_line)
				counters_collection.add_or_update_series(metric_name, parsed_log_line)
				log_timestamp = parser.parse_timestamp(line)

				if log_timestamp > current_time:
					current_time = log_timestamp

				# if something is finally greater than or equal to 10 away from current_time,
				# do the alertmanager summaries

				# last_ten_second_count = counters_collection.total_count_since(10, current_time, '404')
				# if last_ten_second_count > 0:
				# 	print(f"current total 400s count in the last ten seconds: {last_ten_second_count}")
			except ValueError as e:
				print(f"Problem log line at {reader.line_num}")
				next

if __name__ == "__main__":
	main()
