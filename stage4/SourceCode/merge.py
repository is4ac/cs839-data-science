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
    # Generate features set F
    F = em.get_features_for_matching(A, B, validate_inferred_attr_types = False)
    # Convert I to a set of feature vectors using F
    H = em.extract_feature_vecs(I, feature_table = F, attrs_after = 'label',
                                show_progress = False)
    excluded_attributes = ['_id', 'l_id', 'r_id', 'label']
    # Fill in missing values with column's average
    H = em.impute_table(H, exclude_attrs = excluded_attributes,
                        strategy='mean')
    # Create and train a logistic regression - the best matcher from stage3.
    lg = em.LogRegMatcher(name='LogReg', random_state=0)
    lg.fit(table = H, exclude_attrs = excluded_attributes, target_attr = 'label')
    # Read in the candidate tuple pairs.
    C = em.read_csv_metadata(FOLDER+'C.csv', key = '_id', ltable = A, rtable = B,
                             fk_ltable = 'l_id', fk_rtable = 'r_id') # labeled data
    # Convert C into a set of features using F
    L = em.extract_feature_vecs(C, feature_table = F, show_progress = False)
    # Fill in missing values with column's average
    L = em.impute_table(L, exclude_attrs=['_id', 'l_id', 'r_id'], 
                        strategy='mean')
    # Predict on L with trained matcher
    predictions = lg.predict(table = L, 
                             exclude_attrs=['_id', 'l_id', 'r_id'], 
                             append = True, target_attr = 'predicted',
                             inplace = False, return_probs = False, 
                             probs_attr = 'proba')
    # Output the merged table (Basically what matches).
    matched_pairs = predictions[predictions.predicted==1]
    left_ids = matched_pairs['l_id'].to_frame()
    left_ids.columns = ['id']
    merged_table = pd.merge(A, left_ids, on='id')
    merged_table.to_csv(FOLDER+'E.csv', index = False)
    
if __name__ == '__main__':
    main()
