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
from sklearn.model_selection import KFold, cross_val_score, cross_val_predict
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
    id = df[list(df.columns[:3])]
    return data, labels, id

def split_data(data, labels, ids, folds):
    # first split data into k folds
    kf = KFold(n_splits = folds)
    train_data_list = []
    train_labels_list = []
    test_data_list = []
    test_labels_list = []
    train_id_list = [] # to trace back the instances id
    test_id_list = []
    for train_index, test_index in kf.split(data, labels):
        train_data, test_data = data.iloc[train_index], data.iloc[test_index]
        train_labels, test_labels = labels.iloc[train_index], labels.iloc[test_index]
        train_id, test_id = ids.iloc[train_index], ids.iloc[test_index]
        train_data_list.append(train_data)
        train_labels_list.append(train_labels)
        test_data_list.append(test_data)
        test_labels_list.append(test_labels)
        train_id_list.append(train_id)
        test_id_list.append(test_id)
    return train_data_list, train_labels_list, test_data_list,\
           test_labels_list, train_id_list, test_id_list
    
def cross_validation(train_data_list, train_labels_list, test_data_list,\
                     test_labels_list, classifier, folds):
    if classifier == 'dt':
        # use decision tree 
        clf = tree.DecisionTreeClassifier()
    elif classifier == 'rf':
        # use random forest 
        clf = RandomForestClassifier()
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
    predictions = []
    for i in range(0, folds):
        train_data, test_data = train_data_list[i], test_data_list[i]
        train_labels, test_labels = train_labels_list[i], test_labels_list[i]
        features = train_data.columns[3:-1]
        
        clf.fit(train_data, train_labels)
        test_predict = clf.predict(test_data)
        test_predict = convert_to_binary(test_predict)
        precisions.append(precision_score(test_labels, test_predict))
        recalls.append(recall_score(test_labels, test_predict))
        predictions.append(test_predict)
    avg_P = numpy.mean(precisions)
    avg_R = numpy.mean(recalls)
    return avg_P, avg_R, predictions

def convert_to_binary(list):
    new_list = []
    for n in list:
        if n < 0.5:
            new_list.append(0)
        else:
            new_list.append(1)

    return new_list

def write_to_file(test_data, test_labels, test_ids, test_predictions, filename):
    # write result of CV to file
    # concatente test instances
    data = pd.DataFrame(test_data[0])
    data = data.append(test_data[1:])
    # concatenate labels
    labels = pd.concat(test_labels, axis = 0)
    # concatenate ids
    ids = pd.DataFrame(test_ids[0])
    ids = ids.append(test_ids[1:])
    dfs = [ids, data, labels]
    for classifier in test_predictions.keys():
        predictions = []
        for i in range(0, FOLDS):
            predictions.extend(test_predictions[classifier][i])
        predictions = pd.DataFrame({classifier: predictions}) 
        dfs.append(predictions)    
    df = pd.concat(dfs, axis = 1)
    df.to_csv(filename, index = False)
    
    
def main():
    # get train data and labels:
    data, labels, ids = read_data('train_data.csv')
    # split data into folds
    train_data, train_labels, test_data, test_labels, train_ids, test_ids =\
                split_data(data, labels, ids, FOLDS)
    # don't do svm, takes too long and inaccurate
    #classifiers = ['dt', 'rf', 'svm', 'linReg', 'logReg']
    classifiers = ['dt', 'rf', 'linReg', 'logReg']
    precisions = [] # list of precisions from classifiers
    recalls = [] # list of recalls from classifiers
    F1scores = [] 
    predictions = {}
    for classifier in classifiers:
        P, R, preds = cross_validation(train_data, train_labels, test_data,\
                                 test_labels, classifier, FOLDS)
        precisions.append(P)
        recalls.append(R)
        predictions[classifier] = preds
        F1 = 2*P*R/(P+R)
        F1scores.append(F1)
        print ('P, R, and F1 scores for classifier {} are: '.format(classifier), P, R, F1) 
        
    bestP_id = precisions.index(max(precisions))
    bestR_id = recalls.index(max(recalls))
    bestP_clf = classifiers[bestP_id]
    bestR_clf = classifiers[bestR_id]
    bestF1_id = F1scores.index(max(F1scores))
    bestF1_clf = classifiers[bestF1_id]
    #print('%s has the highest precision score %s' % (bestP_clf, max(precisions)))
    #print('%s has the highest recall score %s' % (bestR_clf, max(recalls)))
    print('%s has the highest F1 score %s' % (bestF1_clf, max(F1scores)))
    write_to_file(test_data, test_labels, test_ids, predictions, DATA+'results.csv')
    
##   
### debugging
##df = pd.read_csv(DATA + 'train_data.csv')
##data, labels = read_data('train_data.csv')
##splitclf = RandomForestClassifier()
##
##predictions = cross_val_predict(clf, data, labels, cv = 5)
##df = pd.DataFrame((data, labels, predictions)

if __name__ == "__main__":
    df = main()
    
