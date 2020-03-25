def date_to_str(d):
    """Convert date and datetime objects to a string
    Note, this does not do any timezone conversion.
    :param d: The :class:`datetime.date` or :class:`datetime.datetime` to
              convert to a string
    :returns: The string representation of the date
    """
    return d.strftime("%Y-%m-%dT%H:%M:%SZ")