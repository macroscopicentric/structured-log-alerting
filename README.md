# Structured Log Alerting

This is a toy project to parse a web server's access logs and then alert on specific metrics as the log is streamed.

## Installation

This project depends on [poetry](https://python-poetry.org/). Once you have poetry installed, install Structured Log Alerting's dependencies:

```sh
poetry install
```

## Usage

To run the program, you must hand it a log file as a CLI argument. The program expects the log file to be in a strict CSV format with specific fields a la (a preformatted) nginx's access logs. `example_log.csv` is stored in this repo as an example of the expected format and fields.

To invoke the program:
```sh
poetry run main [csv_log_file_path]
```

## Development

To run the tests:

```sh
poetry run pytest
```

To run mypy:

```sh
poetry run mypy .
```

## Design Choices

Here is a list of design choices I've made throughout this project, either because I thought about my options and chose one or because I didn't know enough about alternatives to pursue them:

Hand-Build vs. Off-The-Shelf: [in all honesty is largely because of grading but i'd never want to hand-build most of this IRL - some examples include tinyfluxdb instead of building my own shitty tsdb and probably using pandas or something else to do more sophisticated label and timestamp handling]

Type of Metrics: I've currently only implemented a single metrics type: a monotonically increasing int called "Counter". This is deliberately modeled off Prometheus' metrics rather than statsd or Datadog, simply because that felt like the most applicable pattern for relatively simple request counts like was asked for here. In theory both MetricsCollection and TimeSeries can be subclassed to handle other types of metric in the future (such as gauges or histograms).

Metrics Metadata and Naming: The naming scheme and label tagging is a hybrid of the strict hierarchical namespacing seen in graphite/statsd and the labels/tags used by Prometheus. The labels used here are currently largely extraneous, as all matching currently happens on the metric series names. There are pros and cons to both approaches, hence the hybrid approach. Graphite and statsd's hierarchical approach is inflexible; it makes querying on non-name metadata either difficult or impossible (depending on your version of graphite) and it makes it extremely difficult to change your naming scheme later. However, hierarchical names make querying (especially during roll-ups) extremely easy since you can use key/value pairs and hashing with less nesting.

Granularity of Hierarchical Namespacing: Relatedly, I have deliberately chosen to make my hierarchical namespaced metric names less granular than they could be in some cases. While I store the entire endpoint in a label, if the endpoint has subpaths (ex: `/api/user` has a subpath, '/user'), I don't keep the subpaths in the metric name. This is for a couple of reasons. First, the take home didn't require this and I ended up deciding it was unnecessary. Second, it would add complexity specifically because not all endpoints have subpaths, so we'd end up with metric names that don't all have the same level of granularity. I don't think that would be the end of the world (and might be worth implementing in the future) but I decided it wasn't worth potentially making the querying more finicky.

File IO: Because this is a toy project with a static file, I've also left the file reading very simple. It does currently treat the log file as a lightweight stream, and does not read the entire file into memory at once (just one line at a time). But because I'm not storing anything on disk, quitting and reopening the program will lose all progress, and I've deliberately skipped implementing any real streaming behavior as you'd want with a true monitoring and metrics program. So any updates to the on-disk log file after the program starts running will be ignored.

Parsing and Data Expectations: [currently pretty strict wrt file format, fields, and actual parsing. a lot of implicit and explicit expectations. currently tossing out "malformed" lines and just printing a note.]

Datetime Timestamp Storage: A commonly used compression tactic in Time Series Databases is to store deltas of timestamps rather than timestamps themselves (or possibly even deltas of deltas) in order to reduce the amount of space needed when storing each row of data. I haven't bothered with that here although it could absolutely be done. Instead, mostly for my own readability, I've chosen to just store full timestamps as datetime instances.

Interval Granularity: [why 1s instead of 10s - no filtering on write, filtering on read, don't lose info]

Storing Intervals When There's No Data: [whisper and others, incl rrd, store at all intervals, here would be per second because that's the granularity of the data and the smallest requested interval (10s) in the project spec. pros/cons: storing 0s requires writing a lot more - writing every metric on every second regardless of data, although could be helped a bit with a defaultdict, but would allow reads to be much easier since we're only doing seconds - would only ever have to go back in time x time slots (sortedcollections' SortedDict would actually help then)]

Metric Series Size: [no data intervals make this wiggly, i do have a size limit on each series primarily because nothing in the project spec required actual on-disk storage and/or persistence of anything through program restarts, so i'm storing constant size space in mem but not constant time in the past which is a little weird]

Timestamp Data Type: [did datetimes just because it felt better, honestly? could've left as unix timestamp with current implementation, def underusing timestamp info right now]

## TODO

- [ ] allow for use of asyncio or something similar to read active log files
- [ ] make the parsing more robust and potentially less tied to the existing example log file format
- [ ] make the querying more robust and allow querying by label
- [ ] mypy not passing
