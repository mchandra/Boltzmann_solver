import numpy as np
from lts.initialize import f_background, init_velocities

def BGK_collision_operator(config, delta_f_hat):

  mass_particle      = config.mass_particle
  boltzmann_constant = config.boltzmann_constant

  rho_background         = config.rho_background
  temperature_background = config.temperature_background
  
  vel_x, vel_y, vel_z = init_velocities(config)

  dv_x = vel_x[0, 1, 0] - vel_x[0, 0, 0]
  dv_y = vel_y[1, 0, 0] - vel_y[0, 0, 0]
  dv_z = vel_z[0, 0, 1] - vel_z[0, 0, 0]

  tau           = config.tau
  normalization = f_background(config, 1)

  if(config.mode == '3V'):
    delta_rho_hat = np.sum(delta_f_hat) * dv_x * dv_y * dv_z
    delta_v_x_hat = np.sum(delta_f_hat * vel_x) * dv_x * dv_y * dv_z/rho_background
    delta_v_y_hat = np.sum(delta_f_hat * vel_y) * dv_x * dv_y * dv_z/rho_background
    delta_v_z_hat = np.sum(delta_f_hat * vel_z) * dv_x * dv_y * dv_z/rho_background
    delta_T_hat   = np.sum(delta_f_hat * ((vel_x**2 + vel_y**2+vel_z**2)/3 -\
                                          temperature_background
                                          )) * dv_x * dv_y * dv_z/rho_background

    expr_term_1 = 2 * np.sqrt(2) * temperature_background * delta_v_x_hat *\
                      mass_particle**(5/2) * rho_background * vel_x
    expr_term_2 = np.sqrt(2) * delta_T_hat * mass_particle**(5/2) * rho_background * vel_x**2
    expr_term_3 = 2 * np.sqrt(2) * temperature_background * delta_v_y_hat *\
                      mass_particle**2.5 * rho_background * vel_y
    expr_term_4 = np.sqrt(2) * delta_T_hat * mass_particle**(5/2) * rho_background * vel_y**2
    expr_term_5 = 2 * np.sqrt(2) * temperature_background * delta_v_z_hat *\
                      mass_particle**2.5 * rho_background * vel_z
    expr_term_6 = np.sqrt(2) * delta_T_hat * mass_particle**(5/2) * rho_background * vel_z**2
    expr_term_7 = 2 * np.sqrt(2) * temperature_background**2 * delta_rho_hat * \
                      boltzmann_constant * mass_particle**(3/2)
    expr_term_8 = (2 * np.sqrt(2) * temperature_background -\
                   3 * np.sqrt(2) * delta_T_hat
                  ) * temperature_background * boltzmann_constant * \
                      rho_background * mass_particle**(3/2)
    expr_term_9 = -2 * np.sqrt(2) * rho_background * boltzmann_constant * \
                                    temperature_background**2 * mass_particle**(3/2)

    C_f = ((((expr_term_1 + expr_term_2 + expr_term_3 + expr_term_4 +\
             expr_term_5 + expr_term_6 + expr_term_7 + expr_term_8 + expr_term_9
            )*np.exp(-mass_particle/(2*boltzmann_constant*temperature_background) * \
                    (vel_x**2 + vel_y**2 + vel_z**2)))/\
            (8 * np.pi**1.5 * temperature_background**3.5 *\
             boltzmann_constant**2.5 * normalization
            )
          ) - delta_f_hat)/tau
  
  elif(config.mode == '2V'):
    delta_rho_hat = np.sum(delta_f_hat) * dv_x * dv_y * dv_z
    delta_v_x_hat = np.sum(delta_f_hat * vel_x) * dv_x * dv_y * dv_z/rho_background
    delta_v_y_hat = np.sum(delta_f_hat * vel_y) * dv_x * dv_y * dv_z/rho_background
    delta_T_hat   = np.sum(delta_f_hat * (0.5*(vel_x**2 + vel_y**2) -\
                                          temperature_background
                                          )) * dv_x * dv_y * dv_z/rho_background

  
    expr_term_1 = delta_T_hat * mass_particle**2 * rho_background * vel_x**2 
    expr_term_2 = delta_T_hat * mass_particle**2 * rho_background * vel_y**2
    expr_term_3 = 2 * temperature_background**2 * delta_rho_hat * boltzmann_constant * mass_particle
    expr_term_4 = 2 * (delta_v_x_hat * mass_particle**2 * rho_background*vel_x +\
                       delta_v_y_hat * mass_particle**2 * rho_background *vel_y -\
                       delta_T_hat * boltzmann_constant * mass_particle *rho_background
                      )*temperature_background
    
    C_f = (((expr_term_1 + expr_term_2 + expr_term_3 + expr_term_4)/\
            (4*np.pi*boltzmann_constant**2*temperature_background**3)*\
            np.exp(-mass_particle/(2*boltzmann_constant*temperature_background) * \
                  (vel_x**2 + vel_y**2)))/normalization - delta_f_hat)/tau
  
  elif(config.mode == '1V'):
    delta_rho_hat = np.sum(delta_f_hat) * dv_x * dv_y * dv_z
    delta_v_x_hat = np.sum(delta_f_hat * vel_x) * dv_x * dv_y * dv_z/rho_background
    delta_T_hat   = np.sum(delta_f_hat * (vel_x**2 - temperature_background)) *\
                    dv_x * dv_y * dv_z/rho_background
    
    expr_term_1 = np.sqrt(2 * mass_particle**3) * delta_T_hat * rho_background * vel_x**2
    expr_term_2 = 2 * np.sqrt(2 * mass_particle) * boltzmann_constant * delta_rho_hat * \
                  temperature_background**2
    expr_term_3 = 2 * np.sqrt(2 * mass_particle**3) * rho_background * delta_v_x_hat * vel_x * \
                  temperature_background
    expr_term_4 = - np.sqrt(2 * mass_particle) * boltzmann_constant * delta_T_hat *\
                    rho_background * temperature_background
    
    C_f = ((((expr_term_1 + expr_term_2 + expr_term_3 + expr_term_4)*\
           np.exp(-mass_particle * vel_x**2/(2 * boltzmann_constant * temperature_background))/\
           (4 * np.sqrt(np.pi * temperature_background**5 * boltzmann_constant**3)))/\
            normalization - delta_f_hat
           )/tau
          )

  
  return C_f
