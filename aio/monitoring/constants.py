# how far in the past do we fetch the log to compute the stats.
STATS_INTERVAL_S = 10

# how fare in the past do we check the requests threshold.
ISSUE_INTERVAL_S = 120
STATS_TASK_SCHEDULE_S = 10

# arbitrary choice, which should be tuned according to expected
# log size and memory consumption.
QUEUE_SIZE = 1000
MAX_STATS_LIST_SIZE = ISSUE_INTERVAL_S // STATS_INTERVAL_S
