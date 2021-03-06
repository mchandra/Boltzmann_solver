import arrayfire as af
import numpy as np

from bolt.lib.physical_system import physical_system
from bolt.lib.nonlinear.nonlinear_solver import nonlinear_solver
from bolt.lib.linear.linear_solver import linear_solver

import input_files.domain as domain
import input_files.boundary_conditions as boundary_conditions
import input_files.params as params
import input_files.initialize as initialize

import bolt.src.nonrelativistic_boltzmann.advection_terms as advection_terms
import bolt.src.nonrelativistic_boltzmann.collision_operator as collision_operator
import bolt.src.nonrelativistic_boltzmann.moments as moments

N = 2**np.arange(5, 10)

for i in range(N.size):

    domain.N_q1 = int(N[i])
    # Defining the physical system to be solved:
    system = physical_system(domain,
                             boundary_conditions,
                             params,
                             initialize,
                             advection_terms,
                             collision_operator.BGK,
                             moments
                            )

    nls = nonlinear_solver(system)

    # Timestep as set by the CFL condition:
    dt = params.N_cfl * min(nls.dq1, nls.dq2) \
                      / max(domain.p1_end + domain.p2_end + domain.p3_end)

    time_array = np.arange(0, params.t_final + dt, dt)

    # Checking that time array doesn't cross final time:
    if(time_array[-1]>params.t_final):
        time_array = np.delete(time_array, -1)

    for time_index, t0 in enumerate(time_array[1:]):
        print('Computing For Time =', t0)
        nls.strang_timestep(dt)

    nls.dump_moments('dump/N_%04d'%(int(N[i])))
