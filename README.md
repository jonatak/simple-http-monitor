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

## Code Style

The code style was validated using `pycodestyle`.

## Implementation

I choose to use asyncio to implement the task and consumer logic, as 3 main I/O
type operation is used in this application:

* Reading the access log file
* sleep operation (used to schedule tasks)
* Printing generated message to stdout.

the library `click` is use to parse command line arguments.

## Possible improvement

This application is composed of a unique process which read logs and create alerts,
there are several points which will need to be improved for a real life usage:

* Alerts and logs are not persistent, a data store could be used to store log lines,
and alerts, I started to do the implementation of the current project using elasticsearch,
but roll back to a simpler version when I realised that it was outside the scope of this test.
* Consumer, stats and alerting should be separated process, as it will be easier
to add a remote data store that way or to add monitoring capabilities.
* We could easily add different kinds of appender in addition to the stdout appender
(mail for example).
* An API could be implemented on top of it, to add the possibility to create an UI
dedicated to the monitoring, this API could also be used by other applications to
implement's logic according to stats and alert.
* There isn't a lot of error handling in this project apart from incorrect log line,
there is a lot of room for improvement here.
* More tests could be added, especially to test the log formatting.
* other input function could be added (consuming from message broker, API endpoint ...)
* we could extends the accepted logging format by giving the possibility to have custom
logging formater function or regular expression.
