import argparse
import csv

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
		number_of_fields = reader.fieldnames()
		for line in reader:
			# there's at least one malformed line in the logfile. i
			# have a couple of options here. i could try doing a full
			# try/except (which would also catch other kinds of malformed
			# data, like if it's not a valid csv-formatted line), or
			# i could hold onto the line and try to combine it with line(s)
			# below it in the file to build a single correct line.
			# but this is both easiest and i think a reasonable pattern
			# in metrics since some lossiness is okay (ie, i'm choosing
			# availabilty over consistency) and we cannot guarantee that
			# we'd end up with a properly formed line at the end of an
			# aggregation attempt.
			if len(line) < number_of_fields:
				next
			# do o11y stuff here
			print(reader.line_num)
			print(line)

if __name__ == "__main__":
	main()
