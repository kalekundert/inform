__version__ = '1.19.1'
__released__ = '2019-10-17'

from .inform import (
    # inform utility functions and classes
    cull, indent, is_collection, is_iterable, is_mapping, is_str, join,
    Color, Info,

    # user utility functions and classes
    columns, conjoin, fmt, full_stop, os_error, plural, ProgressBar,
    render, render_bar,

    # debug functions
    aaa, ppp, ddd, vvv, sss,

    # inform classes
    InformantFactory, Inform, Error,

    # inform functions
    done, terminate, terminate_if_errors, errors_accrued, get_prog_name,

    # built-in informants
    log, comment, codicil, narrate, display, output,
    notify, debug, warn, error, fatal, panic,

    # the currently active informer
    get_informer, set_informer,

    # culprit functions
    set_culprit, add_culprit, get_culprit, join_culprit
)
