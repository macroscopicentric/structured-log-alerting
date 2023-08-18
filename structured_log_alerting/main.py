import argparse
import csv

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

		for line in reader:
			# print(reader.line_num)
			try:
				metric_name, parsed_log_line = parser.parse_nginx_log_line(line)
				counters_collection.add_or_update_series(metric_name, parsed_log_line)
				# print(f"metric: {metric_name}")
				# print(counters_collection.series[metric_name].data_points)
			except ValueError as e:
				next

if __name__ == "__main__":
	main()
