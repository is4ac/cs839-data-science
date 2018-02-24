from sklearn import svm
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score

def get_dev_and_test_data():
    """Divides input data into dev set and test set.
    Returns 'dev_data', 'dev_label', 'test_data', 'test_label'.
    'dev_data' and 'test_data' are array of feature vectors.
    'dev_label' and 'test_label' are array of labels which are either 1 or 0.
    1: input is a person name, 0: input is not a person name."""
    # TODO(TrangVu): ideally, we need to read the csv and perform some
    # kind of randomization to create dev and test sets. For now, we just
    # hardcode the data for end-to-end testing.

    # In this example below, we consider strings with at most two words.
    dev_text = 'Trang, is that professor AnHai Doan?'
    # We hardcode two features: 
    # F1 - is all the first letter of the string capitalized
    # F2 - is the string preceded with a noun that represents people
    # such as 'professor', 'doctor', etc.
    dev_data = [
        [1, 0], # Hey
        [1, 0], # Trang
        [0, 0], # is
        [0, 0], # that
        [0, 0], # professor
        [1, 1], # AnHai
        [1, 0], # Doan
        [1, 0], # Hey Trang
        [0, 0], # is that
        [0, 0], # that professor
        [0, 0], # professor AnHai
        [1, 1], # AnHai Doan
        ]
    dev_labels = [
        0, # Hey
        1, # Trang
        0, # is
        0, # that
        0, # professor
        0, # AnHai
        0, # Doan
        0, # Hey Trang
        0, # is that
        0, # that professor
        0, # professor AnHai
        1, # AnHai Doan
        ]
    test_txt = 'Professor Remzi said Turing is genius'
    test_data = [
        [1, 0], # Professor
        [1, 1], # Remzi
        [0, 0], # said
        [1, 0], # Turing
        [0, 0], # is
        [0, 0], # genius
        [1, 0], # Professor Remzi
        [0, 1], # Remzi said
        [0, 0], # said Turing
        [0, 0], # Turing is
        [0, 0], # is genius
        ]
    test_labels = [
        0, # Professor
        1, # Remzi
        0, # said
        1, # Turing
        0, # is
        0, # genius
        0, # Professor Remzi
        0, # Remzi said
        0, # said Turing
        0, # Turing is
        0, # is genius
        ]
    return dev_data, dev_labels, test_data, test_labels

dev_data, dev_labels, test_data, test_labels = get_dev_and_test_data()
# Fit, predict, and compute precision & recall scores for several classifiers.
#
# Decision tree.
clf = tree.DecisionTreeClassifier()
print(len(dev_data) == len(dev_labels))
clf.fit(dev_data, dev_labels)
test_predict = clf.predict(test_data)
print(test_predict)
precision = precision_score(test_labels, test_predict)
recall = recall_score(test_labels, test_predict)
print('Decision Tree Precision score: {0:0.2f}'.format(precision))
print('Decision Tree Recall score: {0:0.2f}'.format(recall))

# Random forest
clf = RandomForestClassifier(max_depth=2, random_state=0)
clf.fit(dev_data, dev_labels)
test_predict = clf.predict(test_data)
precision = precision_score(test_labels, test_predict)
recall = recall_score(test_labels, test_predict)
print('RandomForest Precision score: {0:0.2f}'.format(precision))
print('RandomForest Recall score: {0:0.2f}'.format(recall))

# Support vector machine
clf.fit(dev_data, dev_labels)
test_predict = clf.predict(test_data)
precision = precision_score(test_labels, test_predict)
recall = recall_score(test_labels, test_predict)
print('SVM Precision score: {0:0.2f}'.format(precision))
print('SVM Recall score: {0:0.2f}'.format(recall))

# Linear regression
clf.fit(dev_data, dev_labels)
test_predict = clf.predict(test_data)
precision = precision_score(test_labels, test_predict)
recall = recall_score(test_labels, test_predict)
print('LinearRegression Precision score: {0:0.2f}'.format(precision))
print('LinearRegression Recall score: {0:0.2f}'.format(recall))

# Logistic regression
clf.fit(dev_data, dev_labels)
test_predict = clf.predict(test_data)
precision = precision_score(test_labels, test_predict)
recall = recall_score(test_labels, test_predict)
print('LogisticRegression Precision score: {0:0.2f}'.format(precision))
print('LogisticRegression Recall score: {0:0.2f}'.format(recall))