#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
In this test, we ensure that the value returned by the function calculate_p()
in linear_solver is consistent with our expected results. Although both the
values checked against and the generated values are essentially the same
formulation, the failure of this test may indicate any accidental changes
that may have been introduced.
"""

# Importing dependencies:
import numpy as np
import arrayfire as af

# Importing solver functions:
from bolt.lib.linear_solver.linear_solver import linear_solver

calculate_p = linear_solver._calculate_p_center    


class test():
    def __init__(self):
        self.p1_start = np.random.randint(-10, -5)
        self.p2_start = np.random.randint(-10, -5)
        self.p3_start = np.random.randint(-10, -5)

        self.p1_end = np.random.randint(5, 10)
        self.p2_end = np.random.randint(5, 10)
        self.p3_end = np.random.randint(5, 10)

        self.N_p1 = np.random.randint(16, 32)
        self.N_p2 = np.random.randint(16, 32)
        self.N_p3 = np.random.randint(16, 32)

        self.dp1 = (self.p1_end - self.p1_start) / self.N_p1
        self.dp2 = (self.p2_end - self.p2_start) / self.N_p2
        self.dp3 = (self.p3_end - self.p3_start) / self.N_p3


def test_calculate_p():
    obj = test()

    p1, p2, p3 = calculate_p(obj)

    p1_expected = obj.p1_start + (0.5 + np.arange(obj.N_p1)) * obj.dp1
    p2_expected = obj.p2_start + (0.5 + np.arange(obj.N_p2)) * obj.dp2
    p3_expected = obj.p3_start + (0.5 + np.arange(obj.N_p3)) * obj.dp3

    p2_expected, p1_expected, p3_expected = np.meshgrid(p2_expected,
                                                        p1_expected,
                                                        p3_expected
                                                       )
    
    p1_expected = af.reorder(af.flat(af.to_array(p1_expected)),
                             2, 3, 0, 1
                            )
                          
    p2_expected = af.reorder(af.flat(af.to_array(p2_expected)),
                             2, 3, 0, 1
                            )
                         
    p3_expected = af.reorder(af.flat(af.to_array(p3_expected)),
                             2, 3, 0, 1
                            )

    assert(af.sum(af.abs(p1_expected - p1)) == 0)
    assert(af.sum(af.abs(p2_expected - p2)) == 0)
    assert(af.sum(af.abs(p3_expected - p3)) == 0)
