import argparse
import csv
from datetime import datetime, timedelta

from structured_log_alerting.alertmanager import AlertManager
from structured_log_alerting.metricscollection import CountersCollection
from structured_log_alerting.parser import Parser


def main():
    # argparse stuff
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file_location", help="the location of the csv-formatted log file", type=str
    )
    args = parser.parse_args()

    # ideally i'd like to separate the io out of main for a bunch of
    # reasons (readable code, testability) but only opening the file
    # once gets me the perks of an iterable (specifically, the combo
    # of line buffering + line tracking with the power of #__next__())
    # and i'm not sure how to get that without basically reimplementing
    # this as a class that manually reinvents all of that or using something
    # more formal like asyncio to handle file opening closing.
    with open(args.file_location) as f:
        reader = csv.DictReader(f)

        counters_collection = CountersCollection()
        parser = Parser(reader.fieldnames)
        interesting_counters = ["404", "500"]
        alertmanager = AlertManager(counters_collection, interesting_counters)
        current_time = datetime.min
        start_of_current_ten_second_interval = 0
        ten_seconds_in_timedelta = timedelta(seconds=10)

        for line in reader:
            try:
                metric_name, parsed_log_line = parser.parse_log_line(line)
                counters_collection.add_or_update_series(metric_name, parsed_log_line)
                log_timestamp = parser.parse_timestamp(line)

                if log_timestamp > current_time:
                    # our only (and therefore best) proxy of "the present" is
                    # just whatever latest timestamp we've ever seen. if we
                    # do see a later timestamp, we can assume "the present"
                    # has moved forward. but that's the best info we've got.
                    current_time = log_timestamp
                    alert_message = alertmanager.check_for_elevated_requests(
                        current_time
                    )
                    if len(alert_message) > 0:
                        print(alert_message)

                    # all of this timekeeping is clumsy but also feels good
                    # enough. i think my next step would be something like a
                    # pointer or two stored on disk if/when we started treating
                    # this like a proper tsdb that stored other things on disk.
                    # a persistent pointer also starts to feel like yet another
                    # place where we actually have a producer/consumer model
                    # like a queue.
                    if start_of_current_ten_second_interval == 0:
                        start_of_current_ten_second_interval = current_time

                    if (
                        start_of_current_ten_second_interval + ten_seconds_in_timedelta
                        <= current_time
                    ):
                        # if it's been 10+ seconds since our last summary:
                        summary = alertmanager.provide_summary_for_interval(current_time)
                        for line in summary:
                            print(line)
                        start_of_current_ten_second_interval = current_time

            except ValueError as e:
                print(f"Problem log line at {reader.line_num}")


if __name__ == "__main__":
    main()
