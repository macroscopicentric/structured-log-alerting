# Structured Log Alerting

This is a toy project to parse a web server's access logs and then alert on specific metrics as the log is streamed. By default, the behavior in main.py is to mimic simple file streaming using Python's basic file objects, to print summaries every ten seconds, and to alert when the rps from the log goes above a certain threshold.

## Installation

This project depends on [poetry](https://python-poetry.org/). Once you have poetry installed, install Structured Log Alerting's dependencies:

```sh
poetry install
```

## Usage

To run the program, you must hand it a log file as a CLI argument. The program expects the log file to be in a strict CSV format with specific fields a la (a preformatted) nginx's access logs. `example_log.csv` is stored in this repo as an example of the expected format and fields. If you've received a zipped copy of the entire project, there will be a second file called `log.csv` that you'll want to use to fully test the code.

To invoke the program:
```sh
poetry run main [csv_log_file_path]
```

## Development

To run the tests:

```sh
poetry run pytest
```

mypy is currently installed to verify type hinting but doesn't fully pass. To run mypy to see current type errors:

```sh
poetry run mypy .
```

This repo is also formatted with default `black` formatting. To format files after changes:

```sh
poetry run black .
```

Note: The repo also uses numpydoc-compliant docstrings, but numpydoc is not installed. Installing numpydoc and verifying the docstring formatting would be a useful next step.

## Design Choices

Here is a list of design choices I've made throughout this project, either because I thought about my options and chose one or because I didn't know enough about alternatives to pursue them:

Hand-Build vs. Off-The-Shelf: I wouldn't normally build what is essentially the world's hackiest TSDB by hand. My assumption for this take home exercise was that the goal was to see if I understood and could execute the principles of a basic monitoring and alerting framework. But in a normal production environment, I'm much more inclined to use a pre-built TSDB. If I were making this project for myself, I'd probably use something like tinyfluxdb to handle the TSDB work, and possibly a more robust and well-supported python library like pandas to manage timestamps and some other things.

Type of Metrics: I've currently only implemented a single metrics type: a monotonically increasing int called "Counter". This is deliberately modeled off Prometheus' metrics rather than statsd or Datadog, simply because that felt like the most applicable pattern for relatively simple request counts like was asked for here. In theory both MetricsCollection and TimeSeries can be subclassed to handle other types of metric in the future (such as gauges or histograms).

Metrics Metadata and Naming: The naming scheme and label tagging is a hybrid of the strict hierarchical namespacing seen in graphite/statsd and the labels/tags used by Prometheus. The labels used here are currently largely extraneous, as all matching currently happens on the metric series names. There are pros and cons to both approaches, hence the hybrid approach. Graphite and statsd's hierarchical approach is inflexible; it makes querying on non-name metadata either difficult or impossible (depending on your version of graphite) and it makes it extremely difficult to change your naming scheme later. However, hierarchical names make querying (especially during roll-ups) extremely easy since you can use key/value pairs and hashing with less nesting.

Granularity of Hierarchical Namespacing: Relatedly, I have deliberately chosen to make my hierarchical namespaced metric names less granular than they could be in some cases. While I store the entire endpoint in a label, if the endpoint has subpaths (ex: `/api/user` has a subpath, '/user'), I don't keep the subpaths in the metric name. This is for a couple of reasons. First, the take home didn't require this and I ended up deciding it was unnecessary. Second, it would add complexity specifically because not all endpoints have subpaths, so we'd end up with metric names that don't all have the same level of granularity. I don't think that would be the end of the world (and might be worth implementing in the future) but I decided it wasn't worth potentially making the querying more finicky.

File IO: Because this is a toy project with a static file, I've also left the file reading very simple. It does currently pretend the log file is a lightweight stream, and does not read the entire file into memory at once (just one line at a time). There are also no threads or forks or queues, all of which would help this scale and be more flexible. But because I'm not storing anything on disk, quitting and reopening the program will lose all progress, and I've deliberately skipped implementing any real streaming behavior as you'd want with a true monitoring and metrics program. Any updates to the on-disk log file after the program starts running will be ignored.

Parsing and Data Expectations: The parsing is currently very inflexible, and expects a file to be in exactly the format of the example and log file of the take home. Right now, the program throws out any line it can't parse into a dictionary with the expected fields. This is deliberate, both in the interest of time, but also because if this project became a fully-fledged monitoring tool, parsing metrics out of log files would likely become a totally separate task done by a separate program so it could be co-located with the hosts providing the metrics. So in the case of scaling, it's more likely this program wouldn't need to do any direct file parsing (although it would still need to do some data validation).

Datetime Timestamp Storage: A commonly used compression tactic in Time Series Databases is to store deltas of timestamps rather than timestamps themselves (or possibly even deltas of deltas) in order to reduce the amount of space needed when storing each row of data. I haven't bothered with that here although it could absolutely be done. Instead, mostly for my own readability, I've chosen to just store full timestamps as datetime instances.

Interval Granularity: My interval granularity is currently hardcoded to the most granular level I was provided, which is 1s intervals. This is likely unnecessarily granular given human responsiveness at the end of an alert, and potentially inefficient due to the amount of memory it needs per metric series. But it means we don't lose any information that could be useful in the future, and it shifts complexity from writes (which we'd need for larger interval aggregation) to reads (querying for the 10s summaries is a little more complicated). Generally in a monitoring system I assume writes are much heavier than reads, so I'm comfortable with this tradeoff.

Storing Intervals When There's No Data: Graphite's Whisper database and RRD both store intervals for every series regardless of whether they have data for that interval. This is part of Whisper's promise of maintaining a constant size, since if you don't store every interval but have a size limit on your series data, you can't make any guarantees about storing a constant time interval across the entire series (writing over it later could easily change the time interval represented by the overall series). Here, storing every timestamp would require not only more storage, but would also require more write work generally to populate each series with the new timestamp as time advances forward. Like interval granularity (see above), adding every interval to every series would increase the work required on writes and would simplify reads and queries. If I had chosen to store every interval, for example, I wouldn't even need to filter each series by timestamp to find relevant counts for the interval in a query; instead I could just fetch the x most recent data points. Not storing intervals with no data was much simpler to execute in a toy project, but isn't necessarily the right choice for a production environment where it may be much more important to have bounded disk size guarantees.

Metric Series Size: Because none of the data in this toy project ever needs to be stored on disk, the only reason we need to retain data for any length of time is just to do immediate time aggregations for alerting. As a result, we never need to store data longer than the longest alert threshold (here, the default is two minutes). But because I chose not to store intervals with no data, we don't have any guarantee on the time span covered by a single series, and none of the series are guaranteed to have the same time span. I've added a maximum length to each series, but it's mostly to manage size in memory, and should not be considered a reliable proxy for the time interval covered by stored data. This, like not storing intervals with no data (above) should be considered an effect of building a toy program in a short period of time and not best practices in a true production environment.

Timestamp Data Type: I chose to use internal python datetimes here rather than leaving timestamps as Unix epoch mostly for readability. It was helpful to have readable, printable timestamps while debugging. I'm definitely underusing python's datetimes, and I could probably do more sophisticated things with them than I'm currently doing (especially if I used an additional third-party library like pandas or dateutil). But it makes timestamps standardized, validated within the program after parsing, and easy to convert to other formats.

## Quality of Life Wishlist:

- [ ] add a fuller CLI that includes the ability to turn each "alert" (the 10s summaries and the elevated traffic) on and off.
- [ ] allow for use of asyncio or something similar to read active log files
- [ ] make the parsing more robust and potentially less tied to the existing example log file format
- [ ] allow more flexible interval granularity
- [ ] make the querying more robust and allow querying by label
- [ ] fix the remaining mypy errors
- [ ] install numpydoc and enforce docstring formatting
