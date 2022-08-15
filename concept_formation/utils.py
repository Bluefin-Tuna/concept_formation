"""
The utils module contains a number of utility functions used by other modules.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from numbers import Number
from random import uniform
from random import choice, sample
from itertools import chain, islice, tee
from math import sqrt
from math import isnan


# A hashtable of values to use in the c4(n) function to apply corrections to
# estimates of std.
c4n_table = {2: 0.7978845608028654,
             3:  0.886226925452758,
             4:  0.9213177319235613,
             5:  0.9399856029866254,
             6:  0.9515328619481445,
             7:  0.9593687886998328,
             8:  0.9650304561473722,
             9:  0.9693106997139539,
             10: 0.9726592741215884,
             11: 0.9753500771452293,
             12: 0.9775593518547722,
             13: 0.9794056043142177,
             14: 0.9809714367555161,
             15: 0.9823161771626504,
             16: 0.9834835316158412,
             17: 0.9845064054718315,
             18: 0.985410043808079,
             19: 0.9862141368601935,
             20: 0.9869342675246552,
             21: 0.9875829288261562,
             22: 0.9881702533158311,
             23: 0.988704545233999,
             24: 0.9891926749585048,
             25: 0.9896403755857028,
             26: 0.9900524688409107,
             27: 0.990433039209448,
             28: 0.9907855696217323,
             29: 0.9911130482419843}


def c4(n):
    """
    Returns the correction factor to apply to unbias estimates of standard
    deviation in low sample sizes. This implementation is based on a lookup
    table for n in [2-29] and returns 1.0 for values >= 30.
    >>> c4(3)
    0.886226925452758
    """
    if n <= 1:
        raise ValueError("Cannot apply correction for a sample size of 1.")
    else:
        return c4n_table[n] if n < 30 else 1.0


def isNumber(n):
    """
    Check if a value is a number that should be handled differently than
    nominals.
    """
    return (not isinstance(n, bool) and isinstance(n, Number)) and not isnan(n)


def mean(values):
    """
    Computes the mean of a list of values.
    This is primarily included to reduce dependency on external math libraries
    like numpy in the core algorithm.
    :param values: a list of numbers
    :type values: list
    :return: the mean of the list of values
    :rtype: float
    >>> mean([600, 470, 170, 430, 300])
    394.0
    """
    if len(values) <= 0:
        raise ValueError("Length of list must be greater than 0.")

    return float(sum(values))/len(values)


def std(values):
    """
    Computes the standard deviation of a list of values.
    This is primarily included to reduce dependency on external math libraries
    like numpy in the core algorithm.
    :param values: a list of numbers
    :type values: list
    :return: the standard deviation of the list of values
    :rtype: float
    >>> std([600, 470, 170, 430, 300])
    147.32277488562318
    """
    if len(values) <= 0:
        raise ValueError("Length of list must be greater than 0.")

    meanValue = mean(values)
    variance = float(sum([(v - meanValue) * (v - meanValue) for v in
                          values]))/len(values)
    return sqrt(variance)


def weighted_choice(choices):
    """
    Given a list of tuples [(val, weight),...(val, weight)], return a randomly
    chosen value where the choice frequency is proportional to the choice
    weight divided by the sum of all weights. Note, weights must be greater
    than or equal to 0.
    :param choices: A list of tuples
    :type choices: [(val, weight),...(val, weight)]
    :return: A choice sampled from the list according to the weightings
    :rtype: val
    >>> from random import seed
    >>> seed(1234)
    >>> options = [('a',.25),('b',.12),('c',.46),('d',.07)]
    >>> weighted_choice(options)
    'd'
    >>> weighted_choice(options)
    'c'
    >>> weighted_choice(options)
    'a'
    .. seealso::
        :meth:`CobwebNode.sample <concept_formation.cobweb.CobwebNode.sample>`
    """
    total = sum(w for c, w in choices)
    r = uniform(0, total)
    upto = 0
    for c, w in choices:
        if w < 0:
            raise ValueError('All weights must be greater than or equal to 0.')
        if upto + w > r:
            return c
        upto += w
    raise ValueError("Choices cannot be an empty list")


def oslice(iterable, start, *omits):
    """omit_slice
    returns an iterable without the indices specified in omits,
    ending with the final omit
    **omits must be sorted!**"""
    itr = iter(iterable)
    # Sorry about the crazy itertools shenanigans...
    return chain(islice(itr, start, omits[0]),
                 *(islice(itr, 1, cur_omit - prev_omit)
                   for prev_omit, cur_omit in pairwise(omits)))


def skip_slice(iterable, start, end, skip):
    """skip is index of skipped element"""
    # Credit: https://stackoverflow.com/questions/22279809/
    # can-python-slicing-be-used-to-skip-one-specific-element-by-index
    itr = iter(iterable)
    return chain(islice(itr, start, skip), islice(itr, 1, end))


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def most_likely_choice(choices):
    """
    Given a list of tuples [(val, weight),...(val, weight)], returns the value
    with the highest weight. Ties are randomly broken.
    >>> options = [('a',.25),('b',.12),('c',.46),('d',.07)]
    >>> most_likely_choice(options)
    'c'
    >>> most_likely_choice(options)
    'c'
    >>> most_likely_choice(options)
    'c'
    :param choices: A list of tuples
    :type choices: [(val, weight),...(val, weight)]
    :return: the val with the hightest weight
    :rtype: val
    """
    if len(choices) == 0:
        raise ValueError("Choices cannot be an empty list")

    if any(weight < 0 for _, weight in choices):
        raise ValueError('All weights must be greater than or equal to 0')

    # Sorts based on the weights (lambda x: x[1]),
    # then get the value associated with it ([0])
    return random_tiebreaker(
        sorted(choices, reverse=True, key=lambda x: x[1]),
        key=lambda x: x[1])[0]


def random_tiebreaker(dsc_sorted_list, key=lambda x: x):
    """
    Given a nonempty monotonically nonincreasing list, randomly chooses a value
    with the maximum value. When looking for a maximum, use this method to
    break ties. **Always make sure that the key trims irrelevant information
    so tied elements' keys are equal under the '==' operator!**
    :param dsc_sorted_list: A list of tuples
    :type dsc_sorted_list: [any,...any]
    :param key: A function applied before testing values for equality
    :type key: function
    :return: a value with the hightest value, chosen at random
    :rtype: val
    """
    maximum = key(dsc_sorted_list[0])
    # Check for ties
    i = 1
    # i counts the number of values with the same value
    while i < len(dsc_sorted_list) and maximum == key(dsc_sorted_list[i]):
        i += 1

    if i == 1:
        return dsc_sorted_list[0]
    return choice(dsc_sorted_list[0:i])


def tiebreak_top_2(dsc_sorted_list, key=lambda x: x):
    """
    Given a nonempty monotonically nonincreasing list, randomly chooses two
    values: either the maximum and one of the contenders for second highest,
    or otherwise two values with the maximum value. **Always make sure that
    the key trims irrelevant information so tied elements' keys are equal
    under the '==' operator!**
    :param dsc_sorted_list: A list of tuples
    :type dsc_sorted_list: [any,...any]
    :param key: A function applied before testing values for equality
    :type key: function
    :return: a value with the hightest value, chosen at random
    :rtype: [val, val]
    """
    second = key(dsc_sorted_list[1])
    # If the maximum is the strict best...
    if key(dsc_sorted_list[0]) != second:
        return (dsc_sorted_list[0],
                random_tiebreaker(dsc_sorted_list[1:], key=key))

    # Check for ties
    i = 2
    # i counts the number of values with the same value
    while i < len(dsc_sorted_list) and second == key(dsc_sorted_list[i]):
        i += 1

    if i == 2:
        return (dsc_sorted_list[0], dsc_sorted_list[1])
    return sample(dsc_sorted_list[0:i], 2)
