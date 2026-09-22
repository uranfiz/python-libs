from datetime import timedelta

def bytes_to_human(n: int) -> str:
    """convert bytes to human-readable string."""
    symbols = ("B", "KB", "MB", "GB", "TB", "PB")
    prefix = {s: 1 << (i * 10) for i, s in enumerate(symbols)}
    for s in reversed(symbols):
        if n >= prefix[s]:
            return f"{n / prefix[s]:.2f} {s}"
    return "0 B"

def seconds_to_readable(seconds: int) -> str:
    """convert seconds to human-readable string (e.g. '3д 4ч 12м')."""
    delta = timedelta(seconds=seconds)
    days = delta.days
    hours, rem = divmod(delta.seconds, 3600)
    minutes, secs = divmod(rem, 60)
    parts = []
    if days:
        parts.append(f"{days}д")
    if hours:
        parts.append(f"{hours}ч")
    if minutes:
        parts.append(f"{minutes}м")
    parts.append(f"{secs}с")
    return " ".join(parts)
