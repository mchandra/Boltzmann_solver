#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import arrayfire as af

from bolt.lib.utils.fft_funcs import fft2, ifft2
from bolt.lib.utils.broadcasted_primitive_operations import multiply

def dfields_hat_dt(f_hat, fields_hat, self):
    """
    Returns the value of the derivative of the fields_hat with respect to time 
    respect to time. This is used to evolve the fields with time. 
    
    NOTE:All the fields quantities are included in fields_hat as follows:

    E1_hat = fields_hat[0]
    E2_hat = fields_hat[1]
    E3_hat = fields_hat[2]

    B1_hat = fields_hat[3]
    B2_hat = fields_hat[4]
    B3_hat = fields_hat[5]

    Input:
    ------

      f_hat  : Fourier mode values for the distribution function at which the slope is computed
               At t = 0 the initial state of the system is passed to this function:

      fields_hat  : Fourier mode values for the fields at which the slope is computed
                    At t = 0 the initial state of the system is passed to this function:

    Output:
    -------
    df_dt : The time-derivative of f_hat
    """
    eps = self.physical_system.params.eps
    mu  = self.physical_system.params.mu

    B1_hat = fields_hat[3]
    B2_hat = fields_hat[4]
    B3_hat = fields_hat[5]

    if(self.physical_system.params.hybrid_model_enabled == True):
        # curlB_x =  dB3/dq2
        curlB_1 = B3_hat * 1j * self.k_q2
        # curlB_y = -dB3/dq1
        curlB_2 = -B3_hat * 1j * self.k_q1
        # curlB_z = (dB2/dq1 - dB1/dq2)
        curlB_3 = (B2_hat * 1j * self.k_q1 - B1_hat * 1j * self.k_q2)
    
        # c --> inf limit: J = (∇ x B) / μ
        J1_hat = curlB_1 / mu 
        J2_hat = curlB_2 / mu
        J3_hat = curlB_3 / mu

    else:
        
        J1_hat = multiply(self.physical_system.params.charge,
                          self.compute_moments('mom_v1_bulk', f_hat=f_hat)
                         ) 
        J2_hat = multiply(self.physical_system.params.charge,
                          self.compute_moments('mom_v2_bulk', f_hat=f_hat)
                         ) 
        J3_hat = multiply(self.physical_system.params.charge,
                          self.compute_moments('mom_v3_bulk', f_hat=f_hat)
                         ) 

    # Summing along all species:
    J1_hat = af.sum(J1_hat, 1)
    J2_hat = af.sum(J2_hat, 1)
    J3_hat = af.sum(J3_hat, 1)

    # Checking that there is no mean field component:
    # try:
    #     assert(af.mean(af.abs(B1_hat[:, 0, 0])) < 1e-12)
    #     assert(af.mean(af.abs(B2_hat[:, 0, 0])) < 1e-12)
    #     assert(af.mean(af.abs(B3_hat[:, 0, 0])) < 1e-12)
    # except:
    #     raise SystemExit('Linear Solver cannot solve for non-zero mean magnetic fields')

    # Equations Solved:
    # dE1/dt = + dB3/dq2 - J1
    # dE2/dt = - dB3/dq1 - J2
    # dE3/dt = dB2/dq1 - dB1/dq2 - J3

    if(self.physical_system.params.hybrid_model_enabled == True):

        # Using Generalized Ohm's Law for electric field:
        n_i_hat = self.compute_moments('density', f_hat=f_hat)
        v1_hat  = self.compute_moments('mom_v1_bulk', f_hat=f_hat) / n_i_hat
        v2_hat  = self.compute_moments('mom_v2_bulk', f_hat=f_hat) / n_i_hat
        v3_hat  = self.compute_moments('mom_v3_bulk', f_hat=f_hat) / n_i_hat

        # (v X B)_x = B3 * v2 - B2 * v3
        v_cross_B_1 = B3_hat * v2_hat - B2_hat * v3_hat
        # (v X B)_y = B1 * v3 - B3 * v1
        v_cross_B_2 = B1_hat * v3_hat - B3_hat * v1_hat
        # (v X B)_z = B2 * v1 - B1 * v2
        v_cross_B_3 = B2_hat * v1_hat - B1_hat * v2_hat

        # (J X B)_x = B3 * J2 - B2 * J3
        J_cross_B_1 = B3_hat * J2_hat - B2_hat * J3_hat
        # (J X B)_y = B1 * J3 - B3 * J1
        J_cross_B_2 = B1_hat * J3_hat - B3_hat * J1_hat
        # (J X B)_z = B2 * J1 - B1 * J2
        J_cross_B_3 = B2_hat * J1_hat - B1_hat * J2_hat

        T_e = self.physical_system.params.fluid_electron_temperature
        # E = -(v X B) + (J X B) / (en) - T ∇n / (en)
        self.fields_solver.fields_hat[0] = - 0*v_cross_B_1 \
                                           + 0*J_cross_B_1 / multiply(self.physical_system.params.charge, n_i_hat) \
                                           - T_e * 1j * self.k_q1 * n_i_hat / multiply(self.physical_system.params.charge, n_i_hat)

        self.fields_solver.fields_hat[1] = - 0*v_cross_B_2 \
                                           + 0*J_cross_B_2 / multiply(self.physical_system.params.charge, n_i_hat) \
                                           - T_e * 1j * self.k_q2 * n_i_hat / multiply(self.physical_system.params.charge, n_i_hat)

        self.fields_solver.fields_hat[2] = - 0*v_cross_B_3 \
                                           + 0*J_cross_B_3 / multiply(self.physical_system.params.charge, n_i_hat)

        E1_hat = self.fields_solver.fields_hat[0]
        E2_hat = self.fields_solver.fields_hat[1]
        E3_hat = self.fields_solver.fields_hat[2]
 
    else:
    
        E1_hat = fields_hat[0]
        E2_hat = fields_hat[1]
        E3_hat = fields_hat[2]
        
        dE1_hat_dt =  B3_hat * 1j * self.k_q2 / (mu * eps) - J1_hat / eps
        dE2_hat_dt = -B3_hat * 1j * self.k_q1 / (mu * eps) - J2_hat / eps
        dE3_hat_dt =  (B2_hat * 1j * self.k_q1 - B1_hat * 1j * self.k_q2) / (mu * eps) \
                     -J3_hat / eps

    # dB1/dt = - dE3/dq2
    # dB2/dt = + dE3/dq1
    # dB3/dt = - (dE2/dq1 - dE1/dq2)

    dB1_hat_dt = -E3_hat * 1j * self.k_q2
    dB2_hat_dt =  E3_hat * 1j * self.k_q1
    dB3_hat_dt =  E1_hat * 1j * self.k_q2 - E2_hat * 1j * self.k_q1

    if(self.physical_system.params.hybrid_model_enabled == True):
        # Returning zeros for update of electric field when hybrid model is used
        dfields_hat_dt = af.join(0, 
                                 af.join(0, 0 * dB1_hat_dt, 0 * dB2_hat_dt, 0 * dB3_hat_dt),
                                 dB1_hat_dt, dB2_hat_dt, dB3_hat_dt
                                )

    else:
        dfields_hat_dt = af.join(0, 
                                 af.join(0, dE1_hat_dt, dE2_hat_dt, dE3_hat_dt),
                                 dB1_hat_dt, dB2_hat_dt, dB3_hat_dt
                                )

    af.eval(dfields_hat_dt)
    return(dfields_hat_dt)
