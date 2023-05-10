import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial import distance

# NOTE: II
n = 200

meanA = [43, 57]
meanB = [57, 43]

varx = 100
vary = 100
cov = 90

cm = np.array([[varx, cov], [cov, vary]])

xA, yA = np.random.multivariate_normal(meanA, cm, n).T
xB, yB = np.random.multivariate_normal(meanB, cm, n).T

fig, ax = plt.subplots(1, 1, squeeze=False)
ax[0, 0].plot(xA, yA, 'x')
ax[0, 0].plot(xB, yB, 'x')
plt.show()

# NOTE: RB
n = 100

meanA = [25, 50]
meanB = [35, 60]
varx = 5
vary = 100
cov = 0
cm = np.array([[varx, cov], [cov, vary]])
xA1, yA1 = np.random.multivariate_normal(meanA, cm, n).T
xB1, yB1 = np.random.multivariate_normal(meanB, cm, n).T

meanA = [50, 25]
meanB = [60, 35]
varx = 150
vary = 5
cov = 0
cm = np.array([[varx, cov], [cov, vary]])
xA2, yA2 = np.random.multivariate_normal(meanA, cm, n).T
xB2, yB2 = np.random.multivariate_normal(meanB, cm, n).T

fig, ax = plt.subplots(1, 1, squeeze=False)
ax[0, 0].plot(xA1, yA1, 'x', color='C0')
ax[0, 0].plot(xB1, yB1, 'x', color='C1')
ax[0, 0].plot(xA2, yA2, 'x', color='C0')
ax[0, 0].plot(xB2, yB2, 'x', color='C1')
plt.show()

# TODO: get transform stim code from pizza
# TODO: plot stim code etc from pizza
# TODO: add cue column
# TODO: add correct_cat column