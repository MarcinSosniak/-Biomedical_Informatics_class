from sklearn import svm
from sklearn.model_selection import cross_val_score
import matplotlib.pyplot as plt
import numpy as np

float_formatter = lambda x: "%.2f" % x
np.set_printoptions(formatter={'float_kind':float_formatter})

X = [[10,15], [12,14], [13, 15], [12, 17], [13, 19],
     [20,31], [19,27], [21, 25], [20, 29], [22, 26]]        # features
y = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]                          # labels
X = []
y = []
with open('processed.cleveland.data','r') as f:
    for line in f:
        if line.__contains__('?'):
            continue
        split_line= line.split(',')
        X.append(list(map(lambda x: float(x), split_line[:-1])))
        y.append(int(split_line[-1]))


X = np.asarray(X)
y = np.asarray(y)
##
# svm linear -> 0.57
# svm rbf  -> 0.54
# poly 2 -> 0.53 and takes literal ages
#
clf = svm.SVC(kernel='poly',degree=3, gamma='auto')
scores = cross_val_score(clf, X, y, cv=5)
acc = scores.mean()
print('acc: {0:.2f}'.format(acc))

plt.plot(X[:,0], X[:,1],'*')
plt.show()