from datetime import datetime


def convert_timestamp(timestamp: str) -> str:
    ts = int(timestamp)
    seconds = ts // 1_000_000_000
    microseconds = (ts % 1_000_000_000) // 1000
    local_time = (
        datetime.fromtimestamp(seconds)
        .replace(microsecond=microseconds)
        .strftime("%Y-%m-%d %H:%M:%S.%f")
    )
    return local_time
