from datetime import datetime
import pytest


@pytest.fixture
def api_200_metric_name():
    return "api.200"


@pytest.fixture
def api_200_parsed_log():
    return {
        "remotehost": "10.0.0.1",
        "rfc931": "-",
        "authuser": "apache",
        "date": datetime(2019, 2, 7, 16, 18, 58),
        "request": "POST /api/user HTTP/1.0",
        "status": "200",
        "bytes": "1307",
        "http_verb": "POST",
        "section": "api",
        "endpoint": "/api/user",
    }


@pytest.fixture
def api_200_newer_parsed_log():
    return {
        "remotehost": "10.0.0.1",
        "rfc931": "-",
        "authuser": "apache",
        "date": datetime(2019, 2, 7, 16, 18, 59),
        "request": "POST /api/user HTTP/1.0",
        "status": "200",
        "bytes": "1307",
        "http_verb": "POST",
        "section": "api",
        "endpoint": "/api/user",
    }


@pytest.fixture
def report_200_metric_name():
    return "report.200"


@pytest.fixture
def report_200_parsed_log():
    return {
        "remotehost": "10.0.0.1",
        "rfc931": "-",
        "authuser": "apache",
        "date": datetime(2019, 2, 7, 16, 18, 58),
        "request": "POST /report HTTP/1.0",
        "status": "200",
        "bytes": "1307",
        "http_verb": "POST",
        "section": "report",
        "endpoint": "/report",
    }


@pytest.fixture
def report_404_metric_name():
    return "report.404"


@pytest.fixture
def report_404_parsed_log():
    return {
        "remotehost": "10.0.0.4",
        "rfc931": "-",
        "authuser": "apache",
        "date": datetime(2019, 2, 7, 16, 18, 54),
        "request": "POST /report HTTP/1.0",
        "status": "404",
        "bytes": "1307",
        "http_verb": "POST",
        "section": "report",
        "endpoint": "/report",
    }
