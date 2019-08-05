class Future:
    """
    This helper method allows the .items method of Python 3
    to be wrapped to the equivalent .iteritems method
    of Python 2.7

    The code for this method was sourced from Python Future:
    https://python-future.org/

    Python Future is licenced under the MIT Licence. Full licence details
    and credits can be found here:
    https://python-future.org/credits.html
    """
    @staticmethod
    def iteritems(obj, **kwargs):
        func = getattr(obj, "iteritems", None)

        if not func:
            func = obj.items

        return func(**kwargs)
