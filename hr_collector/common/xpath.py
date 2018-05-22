def attr_contains(attr, *args):
    return (" and ".join(["contains(@{}, '{}')".format(attr, arg) for arg in args])).strip()