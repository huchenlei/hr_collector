import time
import random


def random_wait(mean=0, variance=1):
    """
    Apply a random wait time (in seconds) with mean and variance provided
    before calling the function

    :param mean: mean waiting time
    :param variance: variance
    :return: decorator
    """
    def random_wait_decorator(func):
        def wrapped_func(*args, **kwargs):
            time.sleep(abs(random.gauss(mean, variance)))
            return func(*args, **kwargs)
        return wrapped_func
    return random_wait_decorator
