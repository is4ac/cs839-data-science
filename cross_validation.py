'''
This program finds the best classifier using cross validation on train data
Use this for debugging (tweaking features to get P >= 90% and R >= 60%).
'''

#import csv
import numpy
import os
import random
#import tempfile
#import uuid
import pandas as pd
from sklearn.utils import shuffle
from sklearn import svm, tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import KFold
from sklearn.metrics import precision_score, recall_score

# directories
DATA = 'stage1_docs/Data/'
# global variables
FOLDS = 5

def read_data(csv_file):
    csv_file = DATA + csv_file
    df = pd.read_csv(csv_file)
    # shuffle rows
    df = shuffle(df, random_state = 1)
    features = list(df.columns[3:-1]) # indices may change if feature columns change
    data = df[features]
    labels = df['class_label']
    return data, labels

def split_data(data, labels, folds):
    # first split data into k folds
    kf = KFold(n_splits = folds)
    train_data_list = []
    train_labels_list = []
    test_data_list = []
    test_labels_list = []
    for train_index, test_index in kf.split(data, labels):
        train_data, test_data = data.iloc[train_index], data.iloc[test_index]
        train_labels, test_labels = labels.iloc[train_index], labels.iloc[test_index]
        train_data_list.append(train_data)
        train_labels_list.append(train_labels)
        test_data_list.append(test_data)
        test_labels_list.append(test_labels)
    return train_data_list, train_labels_list, test_data_list, test_labels_list
    
def cross_validation(train_data_list, train_labels_list, test_data_list, test_labels_list, classifier, folds):
    if classifier == 'dt':
        # use decision tree 
        clf = tree.DecisionTreeClassifier()
    elif classifier == 'rf':
        # use random forest 
        clf = RandomForestClassifier(n_estimators=10, max_depth=50, random_state=0)
    elif classifier == 'svm':
        # use support vector machine
        clf = svm.SVC()
    elif classifier == 'linReg':
        # use linear regression
        clf = LinearRegression()
    elif classifier == 'logReg':
        clf = LogisticRegression()
    
    precisions = []
    recalls = []
    for i in range(0, folds):
        train_data, test_data = train_data_list[i], test_data_list[i]
        train_labels, test_labels = train_labels_list[i], test_labels_list[i]
        clf.fit(train_data, train_labels)
        test_predict = clf.predict(test_data)
        test_predict = convert_to_binary(test_predict)
        precisions.append(precision_score(test_labels, test_predict))
        recalls.append(recall_score(test_labels, test_predict))
    avg_P = numpy.mean(precisions)
    avg_R = numpy.mean(recalls)
    return avg_P, avg_R

def convert_to_binary(list):
    new_list = []
    for n in list:
        if n < 0.5:
            new_list.append(0)
        else:
            new_list.append(1)

    return new_list

def main():
    # get train data and labels:
    data, labels = read_data('train_data.csv')
    # split data into folds
    train_data_list, train_labels_list, test_data_list, test_labels_list = split_data(data, labels, FOLDS)
    classifiers = ['dt', 'rf', 'svm', 'linReg', 'logReg']
    precisions = [] # list of precisions from classifiers
    recalls = [] # list of recalls from classifiers
    for classifier in classifiers:
        P, R = cross_validation(train_data_list, train_labels_list,
                            test_data_list, test_labels_list, classifier, FOLDS)
        precisions.append(P)
        recalls.append(R)
        print ('P and R for classifier {} are: '.format(classifier), P, R) 
    
    bestP_id = precisions.index(max(precisions))
    bestR_id = recalls.index(max(recalls))
    bestP_clf = classifiers[bestP_id]
    bestR_clf = classifiers[bestR_id]
    print('%s has the highest precision score %s' % (bestP_clf, max(precisions)))
    print('%s has the highest recall score %s' % (bestR_clf, max(recalls)))
   
 
if __name__ == "__main__":
    main()
    
