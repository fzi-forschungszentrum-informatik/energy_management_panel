from datetime import datetime, timezone

def datetime_from_timestamp(timestamp, tz_aware=True):
    """
    Convert timestamp to datetime object.

    Arguments:
    ----------
    timestamp: int
        Milliseconds since 1.1.1970 UTC
    tz_aware: bool
        If true make datetime object timezone aware, i.e. in UTC.

    Returns:
    --------
    dt: datetime object
        Corresponding datetime object
    """
    dt = datetime.fromtimestamp(timestamp / 1000.)
    if tz_aware:
        dt = dt.astimezone(timezone.utc)
    return dt

def datetime_to_pretty_str(dt):
    """
    Convert datetime object to string similar to ISO 8601 but more compact.

    Arguments:
    ----------
    dt: dateime object
        ... for which the string will be generated.

    Returns:
    --------
    dt_str: string
        The pretty string respresentation of the datetime object.
    """
    dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
    return dt_str
