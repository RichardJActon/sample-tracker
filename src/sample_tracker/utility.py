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


def nest_dict(flat_dict, sep='_'):
    """Return nested dict by splitting the keys on a delimiter.

    >>> nest_dict({'title': 'foo', 'author_name': 'stretch',
    ... 'author_zipcode': '06901'})
    {'author': {'name': 'stretch', 'zipcode': '06901'}, 'title': 'foo'}
    """
    tree = {}
    for key, val in flat_dict.items():
        t = tree
        prev = None
        for part in key.split(sep):
            if prev is not None:
                t = t.setdefault(prev, {})
            prev = part
        else:
            t.setdefault(prev, val)
    return tree

# def recursive_update(base, update):
#     """
#     Recursively update dicts, addresses the limitation of the dict update
#     method that it only applies to the depth at which it is used and does not
#     merge child dictionaries
    
#     """
#     # using iterative stack based approach to avoid potentially hitting
#     # python's recursion limit
#     stack = [(base, update)]
#     while stack:
#         current_base, current_update = stack.pop()
#         for key, value in current_update.items():
#             if key in current_base and isinstance(current_base[key], dict) and isinstance(value, dict):
#                 stack.append((current_base[key], value))
#             else:
#                 current_base[key] = value
#     return base   

# borrow from pydantic's implementation 
# available from from pydantic.v1.utils import deep_update but internal and deprecated so may not reliablly survive updates
KeyType = TypeVar('KeyType')
def deep_update(mapping: dict[KeyType, Any], *updating_mappings: dict[KeyType, Any]) -> dict[KeyType, Any]:
    """Recursively merge `updating_mappings` into a shallow copy of `mapping`.
    Nested dictionaries are merged; any other value from a later mapping replaces the existing one.
    """
    updated_mapping = mapping.copy()
    for updating_mapping in updating_mappings:
        for k, v in updating_mapping.items():
            if k in updated_mapping and isinstance(updated_mapping[k], dict) and isinstance(v, dict):
                updated_mapping[k] = deep_update(updated_mapping[k], v)
            else:
                updated_mapping[k] = v
    return updated_mapping

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

