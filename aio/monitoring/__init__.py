""" Main package and entry point of the Simple Monitoring tool

this package is compose of multiple modules, which have seperate role:

    * parser: which is responsible of the parsing logic
    * tasks: which contains each task executed by the application

Usage:

    simple-http-monitor --input-file=<file_to_monitor> \
    --request-threshold=<threshold use to trigger alter and issues>

"""
import asyncio
import logging
import signal
from typing import List
from functools import partial

import click
import colorama

from .tasks import process_file_task, show_messages_task, stats_task
from .constants import STATS_TASK_SCHEDULE_S


logger = logging.getLogger(__name__)
# logger isn't configured and will not display anything in stdout.


async def _shutdown(signal, loop):
    """ Cleanup tasks tied to the service's shutdown. """
    print('Received exit signal %(signal)s...', {
        'signal': signal.name
    })
    tasks = [
        t for t in asyncio.all_tasks()
        if t is not asyncio.current_task()
    ]

    for task in tasks:
        task.cancel()

    print('Cancelling %(task_number)s outstanding tasks', {
        'task_number': len(tasks)
    })
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()


@click.command()
@click.option('--input-file', default='/tmp/access.log',
              help='Path of the file to monitor.')
@click.option('--request-threshold', default=10,
              help='Maximum number of request per second threshold expected')
def main(input_file: str, request_threshold: int):

    # message queue which will be displayed to the user.
    message_queue = asyncio.Queue()

    # queue which contains log line to process.
    log_queue = asyncio.LifoQueue()

    # lock use to make sure tasks doesn't access log_queue simultaneously.
    lock = asyncio.Lock()

    # library use to add color to the output
    colorama.init()

    loop = asyncio.get_event_loop()

    # capture SIGTERM and SIGINT signal for graceful shutdown
    signals = (signal.SIGTERM, signal.SIGINT)

    # add signal handler
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(_shutdown(s, loop))
        )

    # here is the main execution loop, where we create
    # all the task needed for the program to run.
    try:
        # schedule the storing function (log to database).
        loop.create_task(
            process_file_task(message_queue, log_queue, lock, input_file)
        )

        # schedule the stats function every `STATS_TASK_SCHEDULE_S` seconds.
        loop.create_task(
            stats_task(
                STATS_TASK_SCHEDULE_S, message_queue,
                log_queue, lock, request_threshold
            )
        )

        # create the message handler task responsible to display messages.
        loop.create_task(show_messages_task(message_queue))
        loop.run_forever()
    finally:
        loop.close()
        logger.info('Successfully shutdown the service.')
