""" Monitoring task

This module contains all the task runned by simple-http-monitor:

    * process_file_task: a loop which will read every new line in the
      monitored file and store them in Elasticsearch.
    * stats_task: responsible to gather stats about HTTP log and generate
    issues.
    * show_messages: print to stdout messages line generated by other tasks.

"""
import asyncio
import datetime
from collections import Counter, deque

import aiofiles
import rfc3339
from colorama import Fore, Style

from .parser import parse_common, ParserCommonException
from .constants import STATS_INTERVAL_S, MAX_STATS_LIST_SIZE, ISSUE_INTERVAL_S


async def process_file_task(message_queue: asyncio.Queue,
                            log_queue: asyncio.LifoQueue,
                            lock: asyncio.Lock, input_file: str):
    """
        This function will wait for new log line in the `input_file`
        and store them.
    """
    async with aiofiles.open(input_file, 'r') as fd_log:
        while True:
            line = await fd_log.readline()
            line = line.strip()
            if line:
                try:
                    log_line = parse_common(line)
                    async with lock:
                        log_queue.put_nowait(log_line)
                except ParserCommonException as e:
                    await message_queue.put(str(e))


async def show_messages_task(message_queue: asyncio.Queue):
    """Print all messages sent by other tasks"""
    while True:
        print(await message_queue.get())


async def stats_task(task_interval: int, message_queue: asyncio.Queue,
                     log_queue: asyncio.LifoQueue, lock: asyncio.Lock,
                     request_threshold: int):
    """
        this function exists to wrap the creation of the Stats object inside an
        async function,
        and to schedule the task every `task_interval`.
    """
    stats = Stats(message_queue, log_queue, lock, request_threshold)
    while True:
        # Wait for task_interval before processing
        await asyncio.sleep(task_interval)
        await stats.process()


class Stats:
    """ Stats class handle stats and alter logic

    the process methods is responsible to handle:

        * _process_stats
        * _process_issues

    Every STATS_INTERVAL_S seconds, _process_stats will consume log messages
    and generate statistics.

    The result of this process will be store in an internal list.

    _process_issues will check if the sum of requests of this list,
    divided by ISSUE_INTERVAL_S, is over the requests threshold.
    if the result is over threshold an alert will be generated.

    ...

    Methods
    -------
    process()
        Process log lines, and generate stats and alerts.
    """
    def __init__(self, message_queue: asyncio.Queue,
                 log_queue: asyncio.LifoQueue,
                 lock: asyncio.Lock, request_threshold: int):
        self._message_queue = message_queue
        self._log_queue = log_queue
        self._lock = lock
        self._request_threshold = request_threshold
        self._current_issue = False
        self._past_stats = deque(maxlen=MAX_STATS_LIST_SIZE)

    def _get_sync(self):
        line = None
        try:
            line = self._log_queue.get_nowait()
        except asyncio.QueueEmpty:
            line = None
        return line

    def _add_stats(self, stat):
        self._past_stats.append(stat)

    async def _process_issue(self):
        now = rfc3339.now()
        stats_sum = sum(self._past_stats)
        request_rate = stats_sum / ISSUE_INTERVAL_S

        # create issue if request_rate is over threshold and there isn't
        # any existing issues
        if request_rate > self._request_threshold and not self._current_issue:
            self._current_issue = True
            await self._message_queue.put(
                f'{Fore.RED}High traffic generated an alert - hits ='
                f' {stats_sum}, triggered at {now}{Style.RESET_ALL}'
            )

        # resolved issue if request_rate is back to normal
        elif request_rate <= self._request_threshold and self._current_issue:
            self._current_issue = False
            await self._message_queue.put(
                f'{Fore.RED}End of high traffic'
                f' alert at {now}{Style.RESET_ALL}'
            )

    async def _process_stats(self):
        line = self._get_sync()

        # get datetime with timezone offset
        now = rfc3339.now()
        start_stats_date = now - datetime.timedelta(seconds=STATS_INTERVAL_S)
        total_requests_stats = 0
        hits_sections_counter = Counter()

        # lock log_queue, to make sure no messages is added during processing
        async with self._lock:
            while line:
                # skip message which isn't generated during the last 10 seconds
                if line.datetime < start_stats_date:
                    line = self._get_sync()
                    continue
                if now >= line.datetime >= start_stats_date:
                    total_requests_stats += 1
                    section = line.uri.split('/')[1]
                    hits_sections_counter[f'/{section}'] += 1
                line = self._get_sync()

        most_common_section, hits_count = (
            hits_sections_counter.most_common(1)[0]
            if total_requests_stats else (None, None)
        )

        # add stats to the internal stats history, which will be used to
        # generate alerts.
        self._add_stats(total_requests_stats if total_requests_stats else 0)
        if not total_requests_stats:
            await self._message_queue.put(
                f'{Fore.GREEN}No requests received during the last'
                f' {STATS_INTERVAL_S} seconds{Style.RESET_ALL}'
            )
        else:
            await self._message_queue.put(
                f'{Fore.GREEN}{total_requests_stats} requests received'
                f' during the last {STATS_INTERVAL_S} seconds, '
                f'most hits received on endpoint: {most_common_section}'
                f' with {hits_count} requests{Style.RESET_ALL}'
            )

    async def process(self):
        """Main processing methods of Stats class"""
        await self._process_stats()
        await self._process_issue()
