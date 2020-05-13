import asyncio

import rfc3339
import pytest
from colorama import Fore, Style

from aio.monitoring.tasks import Stats
from aio.monitoring.constants import STATS_INTERVAL_S
from aio.monitoring.parser import LogLine

NO_REQUEST_RECEIVED_STRING = (
    f'{Fore.GREEN}No requests received during'
    f' the last {STATS_INTERVAL_S} seconds{Style.RESET_ALL}'
)


def get_stats_object():
    return Stats(asyncio.Queue(), asyncio.LifoQueue(), asyncio.Lock(), 10)


@pytest.mark.asyncio
async def test_no_stats():
    stats = get_stats_object()
    await stats._process_stats()
    assert NO_REQUEST_RECEIVED_STRING == await stats._message_queue.get()


@pytest.mark.asyncio
async def test_small_stats():
    stats = get_stats_object()
    stats._log_queue.put_nowait(LogLine(
        host='127.0.0.1',
        rfc931='-',
        user='james',
        datetime=rfc3339.now(),
        uri='/report',
        method='GET',
        protocol='HTTP/1.0',
        status=200,
        bytes_received=12
    ))
    await stats._process_stats()
    assert (
        f'{Fore.GREEN}1 requests received during the last 10 seconds, most'
        f' hits received on endpoint: /report with 1 requests{Style.RESET_ALL}'
    ) == await stats._message_queue.get()


@pytest.mark.asyncio
async def test_past_stats():
    stats = get_stats_object()
    stats._log_queue.put_nowait(LogLine(
        host='127.0.0.1',
        rfc931='-',
        user='james',
        datetime=rfc3339.parse_datetime('2019-12-15T00:02:50+01:00'),
        uri='/report',
        method='GET',
        protocol='HTTP/1.0',
        status=200,
        bytes_received=12
    ))
    await stats._process_stats()
    assert NO_REQUEST_RECEIVED_STRING == await stats._message_queue.get()


@pytest.mark.asyncio
async def test_alert():
    stats = get_stats_object()
    stats._past_stats.append(3000)
    await stats._process_issue()

    expected_msg = (
        f'High traffic generated an alert -'
        f' hits = {sum(stats._past_stats)}'
    )
    assert expected_msg in await stats._message_queue.get()

    stats._past_stats.pop()
    await stats._process_issue()
    assert 'End of high traffic alert at' in await stats._message_queue.get()


@pytest.mark.asyncio
async def test_full_process():
    stats = get_stats_object()

    for i in range(3000):
        stats._log_queue.put_nowait(
            LogLine(
                host='127.0.0.1',
                rfc931='-',
                user='james',
                datetime=rfc3339.now(),
                uri='/report',
                method='GET',
                protocol='HTTP/1.0',
                status=200,
                bytes_received=12
            )
        )

    await stats.process()
    assert (
        f'{Fore.GREEN}3000 requests received during the last 10 seconds,'
        f' most hits received on endpoint: '
        f'/report with 3000 requests{Style.RESET_ALL}'
    ) == await stats._message_queue.get()

    assert (
        f'High traffic generated an alert - hits = 3000'
        in await stats._message_queue.get()
    )
