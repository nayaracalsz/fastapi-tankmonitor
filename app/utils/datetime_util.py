from datetime import datetime, timezone


def parse_firestore_timestamp(ts) -> datetime:
    if hasattr(ts, "timestamp"):
        return datetime.fromtimestamp(ts.timestamp(), tz=timezone.utc)
    elif isinstance(ts, dict) and "_seconds" in ts:
        return datetime.fromtimestamp(ts["_seconds"], tz=timezone.utc)
    elif isinstance(ts, str):
        return datetime.fromisoformat(ts)
    return datetime.now(datetime.timezone.utc)
