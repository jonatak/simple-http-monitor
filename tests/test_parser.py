import rfc3339
import pytest

from aio.monitoring.parser import (
    parse_common,
    LogLine,
    ParserCommonException
)


def test_simple_log_line():
    line = (
        '127.0.0.1 - james [15/Dec/2019:00:2:50 +0100]'
        ' "GET /report HTTP/1.0" 200 12'
    )
    log_line = parse_common(line)
    assert log_line == LogLine(
        host='127.0.0.1',
        rfc931='-',
        user='james',
        datetime=rfc3339.parse_datetime('2019-12-15T00:02:50+01:00'),
        uri='/report',
        method='GET',
        protocol='HTTP/1.0',
        status=200,
        bytes_received=12
    )


def test_incorrect_log_line():
    line = (
        '127.0.0.1 - james [15/Dec/2019:00:2:50 +0100]'
        ' "GET /report HTTP/1.0" 200'
    )
    with pytest.raises(ParserCommonException):
        log_line = parse_common(line)
