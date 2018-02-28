import csv
import numpy
import os
import tempfile
import uuid
from sklearn import svm
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from featured_data_generator import OTHER_FEATURES
from featured_data_generator import TRAIN_CSV
from featured_data_generator import TEST_CSV
from featured_data_generator import createDevAndTestFileSet
from featured_data_generator import extractAndCreateCSV

def get_feature_and_label_from_file(input_csv_file):
    """Reads a csv file and produce feature vectors and label.
       Converts string features from the file to ints so that they
       can be used with our classifier later on."""
    # If you add more features, please update 'feature_names'.
    data = []
    label = []
    with open(input_csv_file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            features = []
            for feature in OTHER_FEATURES:
                # Here we assume features are int. If we ever change this assumption
                # change this code.
                features.append(int(row[feature]))
            data.append(features)
            label.append(int(row['class_label']))
    return data, label

def get_dev_and_test_data():
    """Returns 'dev_data', 'dev_label', 'test_data', 'test_label'."""
    dev_data, dev_labels = get_feature_and_label_from_file(TRAIN_CSV)
    test_data, test_labels = get_feature_and_label_from_file(TEST_CSV)
    return dev_data, dev_labels, test_data, test_labels
    
def get_hardcoded_dev_and_test_data():
    """Returns 'dev_data', 'dev_label', 'test_data', 'test_label'.
    'dev_data' and 'test_data' are array of feature vectors.
    'dev_label' and 'test_label' are array of labels which are either 1 or 0.
    1: input is a person name, 0: input is not a person name."""
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

def convert_to_binary(list):
    new_list = []
    for n in list:
        if n < 0.5:
            new_list.append(0)
        else:
            new_list.append(1)

    return new_list

def chunkIt(seq, num):
    """Divides list 'seq' into 'num' rougly equal parts. """
    avg = len(seq) / float(num)
    out = []
    last = 0.0
    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out

def create_tmp_files():
    """Returns a unique, non-existing tmp train and test file names."""
    tmp_file = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
    tmp_train = tmp_file + '_train.csv'
    tmp_test = tmp_file + '_test.csv'
    while os.path.isfile(tmp_train) or os.path.isfile(tmp_test):
        tmp_file = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
        tmp_train = tmp_file + '_train.csv'
        tmp_test = tmp_file + '_test.csv'
    return tmp_train, tmp_test

def compute_average_P_and_R(folds, clf):
    """Returns average precision and recall scores given a set of file folds."""
    precisions = []
    recalls = []
    for i in range (0, 5):
        print('Round %s' % (i + 1))
        test_set = folds[i]
        train_set = []
        for j in range (0, 5):
            if (j != i):
                train_set += folds[j]
        train_csv, test_csv = create_tmp_files()
        extractAndCreateCSV(train_set, train_csv)
        extractAndCreateCSV(test_set, test_csv)
        train_data, train_label = get_feature_and_label_from_file(train_csv)
        test_data, test_label = get_feature_and_label_from_file(test_csv)
        clf.fit(train_data, train_label)
        test_predict = clf.predict(test_data)
        test_predict = convert_to_binary(test_predict)
        precisions.append(precision_score(test_label, test_predict))
        recalls.append(recall_score(test_label, test_predict))
        # clean up temporary files.
        os.remove(train_csv)
        os.remove(test_csv)
    avg_P = numpy.mean(precisions)
    avg_R = numpy.mean(recalls)
    print('AVG precision = %s' % avg_P)
    print('AVG recall = %s' % avg_R)
    return avg_P, avg_R

def cross_validation():
    """Performs cross validation on certain classifier 'clf'.
    Returns average precision and recall scores.
    """
    dev_file_set, test_file_set = createDevAndTestFileSet()
    folds = chunkIt(dev_file_set, 5)
    print('Cross Validation for DecisionTree')
    avg_P, avg_R = compute_average_P_and_R(folds, tree.DecisionTreeClassifier())

    max_avg_P = avg_P
    max_avg_R = avg_R
    highest_P_clf = 'DecisionTree'
    highest_R_clf = 'DecisionTree'

    print('Cross Validation for Random Forest')
    avg_P, avg_R = compute_average_P_and_R(folds,
                                           RandomForestClassifier(n_estimators=10,
                                                                  max_depth=50,
                                                                  random_state=0))
    if (max_avg_P < avg_P):
        max_avg_P = avg_P
        highest_P_clf = 'RandomForest'
    if (max_avg_R < avg_R):
        max_avg_R = avg_R
        highest_R_clf = 'RandomForest'

    print('Cross Validation for SVC')
    avg_P, avg_R = compute_average_P_and_R(folds, svm.SVC())
    if (max_avg_P < avg_P):
        max_avg_P = avg_P
        highest_P_clf = 'SVC'
    if (max_avg_R < avg_R):
        max_avg_R = avg_R
        highest_R_clf = 'SVC'

    print('Cross Validation for LinearRegression')
    avg_P, avg_R = compute_average_P_and_R(folds, LinearRegression())
    if (max_avg_P < avg_P):
        max_avg_P = avg_P
        highest_P_clf = 'LinearRegression'
    if (max_avg_R < avg_R):
        max_avg_R = avg_R
        highest_R_clf = 'LinearRegression'

    print('Cross Validation for LogisticRegression')
    avg_P, avg_R = compute_average_P_and_R(folds, LogisticRegression())
    if (max_avg_P < avg_P):
        max_avg_P = avg_P
        highest_P_clf = 'LogisticRegression'
    if (max_avg_R < avg_R):
        max_avg_R = avg_R
        highest_R_clf = 'LogisticRegression'

    print('%s has the highest precision score %s' % (highest_P_clf, max_avg_P))
    print('%s has the highest recall score %s' % (highest_R_clf, max_avg_R))


def main():
    dev_data, dev_labels, test_data, test_labels = get_dev_and_test_data()
    # Fit, predict, and compute precision & recall scores for several classifiers.
    #
    # Decision tree.
    clf = tree.DecisionTreeClassifier()
    clf.fit(dev_data, dev_labels)
    test_predict = clf.predict(test_data)
    precision = precision_score(test_labels, test_predict)
    recall = recall_score(test_labels, test_predict)

    # for debugging purposes
    with open('test_predict.txt', 'w') as file:
        for n in test_predict:
            file.write(str(int(n)) + "\n")
    with open('test_labels.txt', 'w') as file:
        for n in test_labels:
            file.write(str(int(n)) + "\n")

    print('Decision Tree Precision score: {0:0.2f}'.format(precision))
    print('Decision Tree Recall score: {0:0.2f}'.format(recall))

    # Random forest
    clf = RandomForestClassifier(n_estimators=10, max_depth=50, random_state=0)
    clf.fit(dev_data, dev_labels)
    test_predict = clf.predict(test_data)
    precision = precision_score(test_labels, test_predict)
    recall = recall_score(test_labels, test_predict)
    print('RandomForest Precision score: {0:0.2f}'.format(precision))
    print('RandomForest Recall score: {0:0.2f}'.format(recall))

    # Support vector machine
    clf = svm.SVC()
    clf.fit(dev_data, dev_labels)
    test_predict = clf.predict(test_data)
    precision = precision_score(test_labels, test_predict)
    recall = recall_score(test_labels, test_predict)
    print('SVM Precision score: {0:0.2f}'.format(precision))
    print('SVM Recall score: {0:0.2f}'.format(recall))

    # Linear regression
    clf = LinearRegression()
    clf.fit(dev_data, dev_labels)
    test_predict = clf.predict(test_data)
    test_predict = convert_to_binary(test_predict)
    precision = precision_score(test_labels, test_predict)
    recall = recall_score(test_labels, test_predict)
    print('LinearRegression Precision score: {0:0.2f}'.format(precision))
    print('LinearRegression Recall score: {0:0.2f}'.format(recall))

    # Logistic regression
    clf = LogisticRegression()
    clf.fit(dev_data, dev_labels)
    test_predict = clf.predict(test_data)
    test_predict = convert_to_binary(test_predict)
    precision = precision_score(test_labels, test_predict)
    recall = recall_score(test_labels, test_predict)
    print('LogisticRegression Precision score: {0:0.2f}'.format(precision))
    print('LogisticRegression Recall score: {0:0.2f}'.format(recall))

if __name__ == "__main__":
    # main()
    cross_validation()
