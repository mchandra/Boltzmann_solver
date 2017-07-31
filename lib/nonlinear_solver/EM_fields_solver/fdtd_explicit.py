#!/usr/bin/env python 
# -*- coding: utf-8 -*-
import arrayfire as af

def fdtd(self, dt):
    
  # E's and B's are staggered in time such that
  # B's are defined at (n + 1/2), and E's are defined at n 

  # Positions of grid point where field quantities are defined:
  # B1 --> (i, j + 1/2)
  # B2 --> (i + 1/2, j)
  # B3 --> (i + 1/2, j + 1/2)
  
  # E1 --> (i + 1/2, j)
  # E2 --> (i, j + 1/2)
  # E3 --> (i, j)
  
  # J1 --> (i + 1/2, j)
  # J2 --> (i, j + 1/2)
  # J3 --> (i, j)

  # The communicate function transfers the data from the local vectors to the global
  # vectors, in addition to dealing with the boundary conditions:
  self._communicate_fields()

  # dE1/dt = + dB3/dq2
  # dE2/dt = - dB3/dq1
  # dE3/dt = dB2/dq1 - dB1/dq2

  dq1 = self.dq1
  dq2 = self.dq2

  self.E1 +=  (dt/dq2) * (self.B3 - af.shift(self.B3, 0, 1)) - self.J1 * dt
  self.E2 += -(dt/dq1) * (self.B3 - af.shift(self.B3, 1, 0)) - self.J2 * dt
  self.E3 +=  (dt/dq1) * (self.B2 - af.shift(self.B2, 1, 0)) \
             -(dt/dq2) * (self.B1 - af.shift(self.B1, 0, 1)) \
             - dt * self.J3
          
  self._communicate_fields()

  # dB1/dt = - dE3/dq2
  # dB2/dt = + dE3/dq1
  # dB3/dt = - (dE2/dq1 - dE1/dq2)

  self.B1 +=  -(dt/dq2) * (af.shift(self.E3,  0, -1) - self.E3)
  self.B2 +=   (dt/dq1) * (af.shift(self.E3, -1,  0) - self.E3)
  self.B3 += - (dt/dq1) * (af.shift(self.E2, -1,  0) - self.E2) \
             + (dt/dq2) * (af.shift(self.E1,  0, -1) - self.E1)

  af.eval(self.E1, self.E2, self.E3,self.B1, self.B2, self.B3)
  return

def fdtd_grid_to_ck_grid(E1, E2, E3, B1, B2, B3):

  # Interpolating at the (i + 1/2, j + 1/2) point of the grid to use for the nonlinear solver:    
  E1 = 0.5 * (E1 + af.shift(E1,  0, -1)) #(i + 1/2, j + 1/2)
  B1 = 0.5 * (B1 + af.shift(B1, -1,  0)) #(i + 1/2, j + 1/2)

  E2 = 0.5 * (E2 + af.shift(E2, -1,  0)) #(i + 1/2, j + 1/2)
  B2 = 0.5 * (B2 + af.shift(B2,  0, -1)) #(i + 1/2, j + 1/2)

  E3 = 0.25 * (
               E3                  + af.shift(E3,  0, -1) + \
               af.shift(E3, -1, 0) + af.shift(E3, -1, -1)
              ) #(i + 1/2, j + 1/2)

  af.eval(E1, E2, E3, B1, B2)
  return(E1, E2, E3, B1, B2)