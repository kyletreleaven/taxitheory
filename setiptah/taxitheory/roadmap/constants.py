
import numpy as np

# until I find it
NETWORKDISTANCEFACTOR = np.sqrt(2)      # this is approximately right


# Idea:
# 1. Throw points (binomial point proc.)
# 2. Get Delaunay triangulation 
# 3. Multiply edge lengths by i.i.d. r.v., min 1, mean distance factor
