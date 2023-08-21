import pytest

from structured_log_alerting.parser import Parser

@pytest.fixture
def malformed_log_line_a():
	return {
		'remotehost': '10.0.0.5',
		'rfc931': '-',
		'authuser': '',
		'date': None,
		'request': None,
		'status': None,
		'bytes': None
	}

@pytest.fixture
def malformed_log_line_b():
	return {
		'remotehost': 'apache',
		'rfc931': '1549574191',
		'authuser': 'GET /report HTTP/1.0',
		'date': '200',
		'request': '1234',
		'status': None,
		'bytes': None
	}

@pytest.fixture
def correctly_formatted_log_line():
	# api.200
	return {
		'remotehost': '10.0.0.3',
		'rfc931': '-',
		'authuser': 'apache',
		'date': '1549574330',
		'request': 'POST /api/user HTTP/1.0',
		'status': '200',
		'bytes': '1234',
}

def test_parser_raises_on_valuerror(malformed_log_line_a, correctly_formatted_log_line):
	parser = Parser(list(correctly_formatted_log_line))
	with pytest.raises(ValueError):
		metric_name, parsed_log_line = parser.parse_log_line(malformed_log_line_a)

def test_parser_raises_on_attributeerror(malformed_log_line_b, correctly_formatted_log_line):
	# this test is a bit of a misnomer; here we're actually catching
	# an AttributeError but we're choosing to raise a ValueError because
	# that's what that actually is. but i wanted to document the types
	# of real-world scenarios i was running into.
	parser = Parser(list(correctly_formatted_log_line))
	with pytest.raises(ValueError):
		metric_name, parsed_log_line = parser.parse_log_line(malformed_log_line_b)

def test_parser_parses_correctly(correctly_formatted_log_line):
	parser = Parser(list(correctly_formatted_log_line))
	metric_name, parsed_log_line = parser.parse_log_line(correctly_formatted_log_line)

	assert type(metric_name) == str
	assert metric_name.count('.') > 0
	assert type(parsed_log_line) == dict

def test_parser_parses_request_correctly(correctly_formatted_log_line):
	parser = Parser(list(correctly_formatted_log_line))
	parsed_request = parser.parse_request(correctly_formatted_log_line)

	assert 'http_verb' in parsed_request._fields and parsed_request.http_verb == 'POST'
	assert 'section' in parsed_request._fields and parsed_request.section == 'api'
	assert 'endpoint' in parsed_request._fields and parsed_request.endpoint == '/api/user'
	assert 'http_version' in parsed_request._fields and parsed_request.http_version == 'HTTP/1.0'

def test_too_long_timestamp_handles_oserror(capsys, correctly_formatted_log_line):
	invalid_timestamp = "1111111111111111111"
	correctly_formatted_log_line['date'] = invalid_timestamp
	parser = Parser(list(correctly_formatted_log_line))
	timestamp = parser.parse_timestamp(correctly_formatted_log_line)
	out, err = capsys.readouterr()

	assert out == f"Invalid timestamp, failed to parse: {invalid_timestamp}\n"
	assert timestamp == None

def test_invalid_timestamp_handles_valueerror(capsys, correctly_formatted_log_line):
	invalid_timestamp = "33333333333333333"
	correctly_formatted_log_line['date'] = invalid_timestamp
	parser = Parser(list(correctly_formatted_log_line))
	timestamp = parser.parse_timestamp(correctly_formatted_log_line)
	out, err = capsys.readouterr()

	assert out == f"Invalid timestamp, failed to parse: {invalid_timestamp}\n"
	assert timestamp == None
