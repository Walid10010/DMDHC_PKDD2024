import sys
import warnings
from sklearn.datasets import make_blobs, make_moons
import numpy as np
if not sys.warnoptions:
    warnings.simplefilter("ignore")
from ExtrachHCluster import DMDHC
from sklearn.preprocessing import MinMaxScaler
from tree import  cal_dendogram_purity

def SyntheticIntro():
    X, Y = make_moons(250, noise=0.03, random_state=42)
    X2, Y2 = make_blobs(100, center_box=(-.0, 0.0), centers=1, cluster_std=0.05, random_state=42)
    X2 = X2 * 80
    X2[:, 1] = X2[:, 1] + 35
    X = np.append(X * 100, X2, axis=0)
    Y2 = Y2 + np.max(Y) + 1
    Y = np.append(Y, Y2, axis=0)

    X2, Y2 = make_blobs(100, center_box=(-.0, 0.0), centers=1, cluster_std=0.05, random_state=42)
    X2 = X2 * 80
    X2[:, 1] = X2[:, 1] + 35
    X2[:, 0] = X2[:, 0] + 35 + 160
    X = np.append(X, X2, axis=0)
    Y2 = Y2 + np.max(Y) + 1
    Y = np.append(Y, Y2, axis=0)

    X2, Y2 = make_blobs(100, center_box=(-.0, 0.0), centers=1, cluster_std=0.05, random_state=42)
    X2 = X2 * 40
    X2[:, 1] = X2[:, 1] + 100
    X = np.append(X, X2, axis=0)
    Y2 = Y2 + np.max(Y) + 1
    Y = np.append(Y, Y2, axis=0)

    return X, Y

X, Y= SyntheticIntro()
m = MinMaxScaler()
X = m.fit_transform(X)
root, y_pred = DMDHC(X,  int(82 * (1)), float(1.8), 3 / 10, 5)
print('dendrogram_purity',  cal_dendogram_purity(X, Y, root))
