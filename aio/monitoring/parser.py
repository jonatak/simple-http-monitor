""" simple-http-monitor parser utilities

This module contains functions used to normalised a log line.
Each logline is expected to be to the format described here:
https://www.w3.org/Daemon/User/Config/Logging.html.
"""
import re
import datetime
from dataclasses import dataclass


# this regex is to parse a line with the format:
# remotehost rfc931 authuser [date] "request" status bytes
HTTP_LOG_REGEX = re.compile(
    r'(?P<host>[a-z0-9.]+) '
    r'(?P<rfc931>[a-z0-9_-]+) '
    r'(?P<user>[a-z0-9_-]+) '
    r'\[(?P<datetime>\d{1,2}/\w{3}/\d{4}:\d{1,2}:\d{1,2}:\d{1,2} \+\d{4})\] '
    r'"(?P<method>[A-Z]{3,5}) (?P<uri>/\S+) (?P<protocol>[A-Z]+/\d\.\d)" '
    r'(?P<status>\d+) '
    r'(?P<bytes_received>\d+)'
)


INPUT_DATE_FORMAT = '%d/%b/%Y:%H:%M:%S %z'


class ParserCommonException(Exception):
    """Exception raised if a line wasn't parsed successfully"""
    pass


@dataclass
class LogLine:
    """A dataclass object which represent a normalised log line."""
    host: str
    rfc931: str
    user: str
    datetime: datetime.datetime
    method: str
    uri: str
    protocol: str
    status: int
    bytes_received: int


def parse_common(line: str) -> LogLine:
    """
        Return a LogLine object constructed from the log line argument,
        expected format: https://www.w3.org/Daemon/User/Config/Logging.html
    """
    data = HTTP_LOG_REGEX.search(line)
    if not data:
        raise ParserCommonException(f'Incorrect log line format: {line}')
    return LogLine(
        host=data['host'],
        rfc931=data['rfc931'],
        user=data['user'],
        datetime=datetime.datetime.strptime(
            data['datetime'], INPUT_DATE_FORMAT
        ),
        method=data['method'],
        uri=data['uri'],
        protocol=data['protocol'],
        status=int(data['status']),
        bytes_received=int(data['bytes_received'])
    )
