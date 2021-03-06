# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import

import unittest

from blaze import error
from blaze import dshape
from blaze.datashape import unify, unify_simple, dshapes

#------------------------------------------------------------------------
# Tests
#------------------------------------------------------------------------

class TestUnification(unittest.TestCase):

    def test_unify_datashape_promotion(self):
        d1 = dshape('10, T1, int32')
        d2 = dshape('T2, T2, float32')
        [result], constraints = unify([(d1, d2)], [True])
        self.assertEqual(result, dshape('10, 10, float32'))

    def test_unify_datashape_promotion2(self):
        # LHS
        s1 = 'A, B, int32'
        s2 = 'B, 10, float32'

        # RHS
        s3 = 'X, Y, int16'
        s4 = 'X, X, Z'

        # Create proper equation
        d1, d2, d3, d4 = dshapes(s1, s2, s3, s4)
        constraints = [(d1, d3), (d2, d4)]

        # What we know from the above equations is:
        #   1) A coerces to X
        #   2) B coerces to Y
        #   3) 10 coerces to X
        #
        # From this we determine that X must be Fixed(10). We must retain
        # type variable B for Y, since we can only say that B must unify with
        # Fixed(10), but not whether it is actually Fixed(10) (it may also be
        # Fixed(1))

        [arg1, arg2], remaining_constraints = unify(constraints, [True, True])
        self.assertEqual(str(arg1), '10, B, int16')
        self.assertEqual(str(arg2), '10, 10, float32')

    def test_unify_datashape_scalar(self):
        d1 = dshape('1, T1, int32')
        d2 = dshape('float64')
        result = unify_simple(d1, d2)
        self.assertEqual(result, dshape('1, 1, float64'))

    def test_unify_broadcasting1(self):
        ds1 = dshape('A, B, int32')
        ds2 = dshape('K, M, N, float32')
        [result], constraints = unify([(ds1, ds2)], [True])
        self.assertEqual(str(result), '1, A, B, float32')

    def test_unify_broadcasting2(self):
        ds1 = dshape('A, B, C, int32')
        ds2 = dshape('M, N, float32')
        [result], constraints = unify([(ds1, ds2)], [True])
        self.assertEqual(str(result), '1, B, C, float32')

    def test_unify_ellipsis(self):
        ds1 = dshape('A, ..., B, int32')
        ds2 = dshape('M, N, ..., S, T, float32')
        [result], constraints = unify([(ds1, ds2)], [True])
        self.assertEqual(str(result), 'A, N, ..., S, B, float32')

    def test_unify_ellipsis2(self):
        ds1 = dshape('X, Y, float32 -> ..., float32 -> Z')
        ds2 = dshape('10, T1, int32 -> T2, T2, float32 -> R')
        [result], constraints = unify([(ds1, ds2)], [True])
        self.assertEqual(str(result), '10, Y, int32 -> T2, T2, float32 -> Z')

    def test_unify_implements(self):
        d1 = dshape('10, int32')
        d2 = dshape('T, A : numeric')
        [res], constraints = unify([(d1, d2)], [True])
        self.assertEqual(str(res), '10, int32')
        self.assertFalse(constraints)


class TestUnificationErrors(unittest.TestCase):

    def test_unify_datashape_error(self):
        d1 = dshape('10, 11, int32')
        d2 = dshape('T2, T2, int32')
        self.assertRaises(error.UnificationError, unify, [(d1, d2)], [True])

    def test_unify_datashape_error_implements(self):
        d1 = dshape('10, int32')
        d2 = dshape('T, A : floating')
        self.assertRaises(error.UnificationError, unify, [(d1, d2)], [True])


if __name__ == '__main__':
    # TestUnification('test_unify_ellipsis2').debug()
    unittest.main()