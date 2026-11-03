from datetime import (
    datetime,
    timezone,
)
def human_readable_filesize(size_bytes: int) -> str:
    """
    Generate human readable data size units.
    Uses 1024 bytes not 1000.
    Max Prefix TiB
    """
    size_bytesf = float(size_bytes)
    units = ['B', 'KiB', 'MiB', 'GiB', 'TiB']
    idx = 0
    
    while size_bytesf >= 1024.0 and idx < len(units) - 1:
        size_bytesf /= 1024.0
        idx += 1
        
    return f"{size_bytesf:.2f} {units[idx]}"

def naive_utc_timestamp() -> datetime:
    """
    To ensure that the current time is in UTC it should be provided to
    datatime's now function.
    MongoDb only supports naive timestamps recorded in UTC but does not
    explicitly store this timezone information.
    So the timezone must be stripped for the this to serialise to the database
    correctly.
    """
    return datetime.now(tz=timezone.utc).replace(tzinfo=None)

