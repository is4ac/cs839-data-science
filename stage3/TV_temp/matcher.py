# Import py_entitymatching package
import py_entitymatching as em
import os
import pandas as pd

# Specify directory 
FOLDER = './Data/'

# Set seed value (to get reproducible results)
seed = 0

def main():
    # Read in data files
    A = em.read_csv_metadata(FOLDER+'A.csv', key = 'id') # imdb data
    B = em.read_csv_metadata(FOLDER+'B.csv', key = 'id') # tmdb data
    G = em.read_csv_metadata(FOLDER+'G.csv', key = '_id', ltable = A, rtable = B,
                             fk_ltable = 'l_id', fk_rtable = 'r_id') # labeled data
    # Split G into I and J for CV
    IJ = em.split_train_test(G, train_proportion = 0.5, random_state = 0)
    I = IJ['train']
    J = IJ['test']
    # Save I and J to files
    I.to_csv(FOLDER+'I.csv')
    J.to_csv(FOLDER+'J.csv')
    # Generate features set F
    F = em.get_features_for_matching(A, B, validate_inferred_attr_types = False)
    #print(F.feature_name)
    #print(type(F))
    # Convert I to a set of feature vectors using F
    H = em.extract_feature_vecs(I, feature_table = F, attrs_after = 'label', show_progress = False)
    #print(H.head)
    # Check of missing values
    #print(any(pd.notnull(H)))
    excluded_attributes = ['_id', 'l_id', 'r_id', 'label']
    # Fill in missing values with column's average
    H = em.impute_table(H, exclude_attrs = excluded_attributes,
                strategy='mean')
    # Create a set of matchers
    dt = em.DTMatcher(name='DecisionTree', random_state=0)
    svm = em.SVMMatcher(name='SVM', random_state=0)
    rf = em.RFMatcher(name='RF', random_state=0)
    lg = em.LogRegMatcher(name='LogReg', random_state=0)
    ln = em.LinRegMatcher(name='LinReg')
    # Selecting best matcher with CV using F1-score as criteria
    CV_result = em.select_matcher([dt, rf, svm, ln, lg], table = H,
                                  exclude_attrs = excluded_attributes,
                                  k = 10, target_attr = 'label',
                                  metric_to_select_matcher = 'f1',
                                  random_state = 0)
    #print(CV_result['cv_stats']) # RF is the best matcher 
    # Best matcher found is RF, train RF on H
    rf.fit(table = H, exclude_attrs = excluded_attributes, target_attr = 'label')
    # Convert J into a set of features using F
    L = em.extract_feature_vecs(J, feature_table = F, attrs_after = 'label', show_progress = False)
    # Fill in missing values with column's average
    L = em.impute_table(L, exclude_attrs = excluded_attributes,
                strategy='mean')
    # Predict on L
    predictions = rf.predict(table = L, exclude_attrs = excluded_attributes,
                             append = True, target_attr = 'predicted', inplace = False,
                             return_probs = True, probs_attr = 'proba')
    # Evaluate predictions
    eval_result = em.eval_matches(predictions, 'label', 'predicted')
    em.print_eval_summary(eval_result)
    
if __name__ == '__main__':
    main()
    
