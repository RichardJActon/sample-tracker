from flask import request
from werkzeug.datastructures import ImmutableMultiDict
from typing import Any
from datetime import (
    datetime,
    timezone,
)

def args_to_dict(args: ImmutableMultiDict) -> dict[str, Any]:
    """
    Converts Flask Request Arguments to a dictionary
    From the Flask Request Class:
    
    args
        The parsed URL parameters (the part in the URL after the question
        mark).

        By default an
        :class:`~werkzeug.datastructures.ImmutableMultiDict`
        is returned from this function.  This can be changed by setting
        :attr:`parameter_storage_class` to a different type.  This might
        be necessary if the order of the form data is important.

        .. versionchanged:: 2.3
            Invalid bytes remain percent encoded.
            
    :param args:
    :type args: ImmutableMultiDict
    :return:
    :rtype: dict

    :Example:
        >>> from werkzeug.datastructures import MultiDict, ImmutableMultiDict
        >>> x = ImmutableMultiDict(MultiDict([('a', 'b'), ('a', 'c')]))
        >>> args_to_dict(x)
        {'a': 'b'}
    """
    form = {}

    for key in args.keys():
        if key.endswith("[]"):
            form[key[:-2]] = args.getlist(key)
        else:
            form[key] = args.get(key)

    return form

def get_form():
    # In addition to the main arguments we also add the session
    # string from the cookie
    # session = ""

    # if "pims_session_id" in request.cookies:
    #     session = request.cookies["pims_session_id"]

    if request.method == "GET":
        form = args_to_dict(request.args)
        # form["session"] = session
        return form

    elif request.method == "POST":
        form = args_to_dict(request.form)
        # form["session"] = session
        return form


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

