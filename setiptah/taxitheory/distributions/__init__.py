
from interface import *

distributions = {}


from setiptah.taxitheory.euclidean.distributions import *

distributions['PairUniform2'] = PairUniform2()
distributions['PairUniform3'] = PairUniform3()
distributions['Cocentric3_1_2'] = Cocentric3_1_2()
distributions['XO_X_O'] = XO_X_O()


from setiptah.taxitheory.roadmap.distributions import *

roadmap = ACC2014Square()
distributions['PairUniformSquareNet'] = PairUniformRoadmap(roadmap)
distributions['ACC2014'] = ACC2014Distr()

