import numpy as np
import arrayfire as af

#TODO : Not able to import affine from utils. Fix this.
#from bolt.lib.utils.coord_transformation import affine

def affine(q1, q2,
           x_y_bottom_left, x_y_bottom_right, 
           x_y_top_right, x_y_top_left,
           X_Y_bottom_left, X_Y_bottom_right, 
           X_Y_top_right, X_Y_top_left,
          ):

    '''
        Inputs :
            - Grid in q1 and q2
            - coordinates of 4 points on the original grid (x, y)
            - coordinates of the corresponding 4 points on the desired transformed grid (X, Y)
        Output : Transformed grid
    '''
    
    x0, y0 = x_y_bottom_left;  X0, Y0 = X_Y_bottom_left
    x1, y1 = x_y_bottom_right; X1, Y1 = X_Y_bottom_right
    x2, y2 = x_y_top_right;    X2, Y2 = X_Y_top_right
    x3, y3 = x_y_top_left;     X3, Y3 = X_Y_top_left

    
    #x = a0 + a1*X + a2*Y + a3*X*Y
    #y = b0 + b1*X + b2*Y + b3*X*Y
    
    #x0 = a0 + a1*X0 + a2*Y0 + a3*X0*Y0
    #x1 = a0 + a1*X1 + a2*Y1 + a3*X1*Y1
    #x2 = a0 + a1*X2 + a2*Y2 + a3*X2*Y2
    #x3 = a0 + a1*X3 + a2*Y3 + a3*X3*Y3
    
    # A x = b
    A = np.array([[1, X0, Y0, X0*Y0],
                  [1, X1, Y1, X1*Y1],
                  [1, X2, Y2, X2*Y2],
                  [1, X3, Y3, X3*Y3],
                 ])
    b = np.array([[x0],
                  [x1],
                  [x2],
                  [x3]
                 ])

    a0, a1, a2, a3 = np.linalg.solve(A, b)

    a0 = a0[0]
    a1 = a1[0]
    a2 = a2[0]
    a3 = a3[0]
    
    
    #y0 = b0 + b1*X0 + b2*Y0 + b3*X0*Y0
    #y1 = b0 + b1*X1 + b2*Y1 + b3*X1*Y1
    #y2 = b0 + b1*X2 + b2*Y2 + b3*X2*Y2
    #y3 = b0 + b1*X3 + b2*Y3 + b3*X3*Y3

    b = np.array([[y0],
                  [y1],
                  [y2],
                  [y3]
                 ])

    b0, b1, b2, b3 = np.linalg.solve(A, b)

    b0 = b0[0]
    b1 = b1[0]
    b2 = b2[0]
    b3 = b3[0]
    
    
    x = a0 + a1*q1 + a2*q2 + a3*q1*q2
    y = b0 + b1*q1 + b2*q2 + b3*q1*q2
    
    return(x, y)

def get_cartesian_coords(q1, q2, 
                         q1_start_local_left=None, 
                         q2_start_local_bottom=None,
                         return_jacobian = False
                        ):


    q1_midpoint = 0.5*(af.max(q1) + af.min(q1))
    q2_midpoint = 0.5*(af.max(q2) + af.min(q2))

    # Default initializsation to rectangular grid
    x = q1
    y = q2
    
    jacobian = None # Numerically compute the Jacobian
    
    if (q1_start_local_left != None and q2_start_local_bottom != None):

        if ((q2_midpoint < 0.) and (q1_midpoint > -0.5) and (q1_midpoint < 0.)):
            x0 = -0.5; y0 = -1
            x1 = 0;    y1 = -1
            x2 = 0;    y2 = -0.5
            x3 = -0.5; y3 = 0
            x, y = \
              affine(q1, q2, 
               [x0, y0], [x1, y1],
               [x2, y2], [x3, y3],
               [-0.5, -1.], [0, -1],
               [0, 0], [-0.5, 0]
                    )

        elif ((q2_midpoint < 0.) and (q1_midpoint > 0) and (q1_midpoint < 0.5)):

            x0 = 0.;   y0 = -1
            x1 = 0.5;  y1 = -1
            x2 = 0.5;  y2 = 0.
            x3 = -0;   y3 = -0.5
            x, y = \
              affine(q1, q2, 
               [x0, y0], [x1, y1],
               [x2, y2], [x3, y3],
               [0., -1.], [0.5, -1],
               [0.5, 0], [0., 0]
                    )

        if (return_jacobian):
            return (x, y, jacobian)
        else: 
            return(x, y)

    else:
        print("Error in get_cartesian_coords(): q1_start_local_left or q2_start_local_bottom not provided")

