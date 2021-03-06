import numpy as np
import arrayfire as af

rho_background         = 1
temperature_background = 1

fields_type       = 'electrostatic'
fields_initialize = 'fft'
fields_solver     = 'fft'

# Dimensionality considered in velocity space:
p_dim = 1

# Method in q-space
solver_method_in_q = 'FVM'
solver_method_in_p = 'FVM'

riemann_solver_in_q = 'upwind-flux'
riemann_solver_in_p = 'upwind-flux'

reconstruction_method_in_q = 'weno5'
reconstruction_method_in_p = 'weno5'

t_final = 1000
N_cfl   = 0.4

# Number of devices(GPUs/Accelerators) on each node:
num_devices = 1

# Constants:
mass               = [1]
boltzmann_constant = 1
charge             = [-1]
eps                = 1

pert_real = 0.04
pert_imag = 0

k_q1 = 0.3
k_q2 = 0

fields_enabled           = True
source_enabled           = False
instantaneous_collisions = True

# Variation of collisional-timescale parameter through phase space:
@af.broadcast
def tau(q1, q2, p1, p2, p3):
    return (np.inf * q1**0 * p1**0)
