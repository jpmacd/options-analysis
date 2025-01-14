from datetime import datetime


def convert_timstamp(timestamp: str) -> str:
    ts = int(timestamp)
    seconds = ts // 1_000_000_000
    microseconds = (ts % 1_000_000_000) // 1000
    human_readable_time = (
        datetime.utcfromtimestamp(seconds)
        .replace(microsecond=microseconds)
        .strftime("%Y-%m-%d %H:%M:%S.%f")
    )
    return human_readable_time
