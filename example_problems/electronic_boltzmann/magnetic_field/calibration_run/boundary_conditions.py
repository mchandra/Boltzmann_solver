import numpy as np
import arrayfire as af
import domain

in_q1_left   = 'mirror+dirichlet'
in_q1_right  = 'mirror+dirichlet'
in_q2_bottom = 'mirror'
in_q2_top    = 'mirror'

@af.broadcast
def f_left(f, t, q1, q2, p1, p2, p3, params):

    k       = params.boltzmann_constant
    E_upper = params.E_band
    T       = params.initial_temperature
    mu      = params.initial_mu
    
    t     = params.current_time
    omega = 2. * np.pi * params.AC_freq
    
    q2_contact_start = params.contact_start
    q2_contact_end   = params.contact_end
    contact_width    = q2_contact_end - q2_contact_start

    vel_drift_x_in  = params.vel_drift_x_in/contact_width

    if (params.p_space_grid == 'cartesian'):
        p_x = p1 
        p_y = p2
    elif (params.p_space_grid == 'polar2D'):
        p_x = p1 * af.cos(p2)
        p_y = p1 * af.sin(p2)
    else:
        raise NotImplementedError('Unsupported coordinate system in p_space')


    fermi_dirac_in = (1./(af.exp( (E_upper - vel_drift_x_in*p_x - mu)/(k*T) ) + 1.)
                     )
    if params.zero_temperature:
        fermi_dirac_in = fermi_dirac_in - 0.5

    # Contacts on either side of the device

    
    cond = ((params.y >= q2_contact_start) & \
            (params.y <= q2_contact_end) \
           )

    f_left = cond*fermi_dirac_in + (1 - cond)*f


    af.eval(f_left)
    return(f_left)

@af.broadcast
def f_right(f, t, q1, q2, p1, p2, p3, params):

    k       = params.boltzmann_constant
    E_upper = params.E_band
    T       = params.initial_temperature
    mu      = params.initial_mu

    t     = params.current_time
    omega = 2. * np.pi * params.AC_freq

    q2_contact_start = params.contact_start
    q2_contact_end   = params.contact_end
    contact_width    = q2_contact_end - q2_contact_start

    vel_drift_x_out = params.vel_drift_x_out/contact_width
    
    if (params.p_space_grid == 'cartesian'):
        p_x = p1 
        p_y = p2
    elif (params.p_space_grid == 'polar2D'):
        p_x = p1 * af.cos(p2)
        p_y = p1 * af.sin(p2)
    else:
        raise NotImplementedError('Unsupported coordinate system in p_space')

    fermi_dirac_out = (1./(af.exp( (E_upper - vel_drift_x_out*p_x - mu)/(k*T) ) + 1.)
                      )
    if params.zero_temperature:
        fermi_dirac_out = fermi_dirac_out - 0.5

    
    cond = ((params.y >= q2_contact_start) & \
            (params.y <= q2_contact_end) \
           )

    f_right = cond*fermi_dirac_out + (1 - cond)*f

    af.eval(f_right)
    return(f_right)
