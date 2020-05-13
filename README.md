# simple-http-monitor

A toy project to experiment asyncio.
This command-line application will consume an access.log file and generate statistics and alerts.
The access log file should be formatted using [w3c formatted logs](https://www.w3.org/Daemon/User/Config/Logging.html).

## Installation

This project use python3.7, you can install this project using pip,
I'll advise you to set up this project in a virtualenv (using a tool like virtualenvwrapper).

    pip3.7 install -e simple-http-monitor

## Usage

    Usage: simple-http-monitor [OPTIONS]

    Options:
        --input-file TEXT            Path of the file to monitor.
        --request-threshold INTEGER  Maximum number of request per second threshold
                                     expected
        --help                       Show this message and exit.

The default input file used by `simple-http-monitor` is /tmp/access.log.
You can submit your own access.log file:

    simple-http-monitor --input-file=myaccess.log

The alert threshold is default at 10 requests per seconds, this value  can be overriden:

    simple-http-monitor --request-threshold=1

## Test

You can run the test using tox:

    pip install tox
    tox
