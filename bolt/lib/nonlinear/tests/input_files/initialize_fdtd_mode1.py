import numpy as np
import arrayfire as af

def initialize_E(q1, q2, params):
    
    E1 = 0 * q1**0 
    E2 = 0 * q1**0
    E3 = -6 * np.pi * np.sqrt(5/9) * af.cos(  2 * np.pi * q1
                                            + 4 * np.pi * q2
                                           )

    af.eval(E1, E2, E3)
    return(E1, E2, E3)

# def initialize_B(q1, q2, params):

#     dt = params.dt

#     B1 = 0 * q1**0
#     B2 = 0 * q1**0
#     # B3 at n + 1/2
#     B3 = af.exp(-100 * (q1 - 0.5 - 0.5 * dt)**2)
#     # B3 = af.exp(-100 * (q1 - 0.5 + 0.5 * dt)**2)

    # af.eval(B1, B2, B3)
    # return(B1, B2, B3)

# def initialize_A3_B3(q1, q2, params):

#     dt = params.dt

#     A3 = af.cos(2 * np.pi * (q1 - 0.5 * dt))
#     B3 = 0 * q1**0

#     af.eval(A3, B3)
#     return(A3, B3)

def initialize_A3_B3(q1, q2, params):

    dt = params.dt

    A3 = af.sin(  2 * np.pi * (q1 - 0.5 * np.sqrt(5 / 9) * dt)
                + 4 * np.pi * (q2 - 0.5 * np.sqrt(5 / 9) * dt)
               )

    B3 = 0 * q1**0

    af.eval(A3, B3)
    return(A3, B3)
