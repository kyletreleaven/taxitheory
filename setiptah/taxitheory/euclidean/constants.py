
import numpy as np

# Pavone [80]
# A. G. Percus and O. C. Martin.
# Finite size and dimensional dependence of the Eu-clidean traveling salesman problem.
# Physical Review Letters, 76(8):1188-1191, 1996.
BETATSP2 = 0.7120      # \pm 0.0002
BETATSP3 = 0.6972      # \pm 0.0002

# J. Houdayer, J.H. Boutet de Monvel, and O.C. Martin.
# Comparing mean field and euclidean matching problems.
# The European Physical Journal B - Condensed Matter and Complex Systems, 6(3):383-393, 1998.
BETAMATCH3 = 0.7080 # \pm 0.0002






""" LOWER BOUNDS """
# volume of d-dimensional unit sphere
SPHEREVOL2 = np.pi
SPHEREVOL3 = (4./3) * np.pi

# lower bound multiplier \gamma_d = \frac{d}{d+1} V_d^{-1/d}
GAMMA2 = (2./3) * np.power( SPHEREVOL2, -1./2 )
GAMMA3 = (3./4) * np.power( SPHEREVOL3, -1./3 )

