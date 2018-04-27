# Import py_entitymatching package
import py_entitymatching as em
import os
import pandas as pd

# Specify directory 
FOLDER = './Data/'

# Set seed value (to get reproducible results)
seed = 0

def merge_cell(a, b):
    """Returned the merged content of the two cell a and b.
    a and be must be strings likes directors, writers, etc.
    We assume ';' as delimeters."""
    # TODO(all): this is just exact match, literally.
    if (pd.isnull(a)):
        return b
    if (pd.isnull(b)):
        return a
    return ';'.join(set(a.split(';')) | set(b.split(';')))

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
    # We start with rows from A that matches.
    # We then merge value from B into A.
    matched_pairs = predictions[predictions.predicted==1]
    left_ids = matched_pairs['l_id'].to_frame()
    left_ids.columns = ['id']
    merged = pd.merge(A, left_ids, on='id')
    merged.set_index('id', inplace=True)
    B.set_index('id', inplace=True)
    black_list = { 'a872', 'a987' }
    for pair in matched_pairs.itertuples():
        aid = pair.l_id
        bid = pair.r_id
        if (aid in black_list):
            continue
        # Title: keep title from A, if title from B is not an exact matched
        # from A, append B’s title to the alternative title field if B’s title
        # is not already in A’s alternative title.
        m_title = merged.loc[aid, 'title']
        a_title = merged.loc[aid, 'title']
        b_title = B.loc[bid, 'title']
        if (b_title != a_title):
            if pd.isnull(merged.loc[aid, 'alternative_titles']):
                merged.loc[aid, 'alternative_titles'] = b_title
            else:
                alt = set(merged.loc[aid, 'alternative_titles'].split(';'))
                if (b_title not in alt):
                    merged.loc[aid, 'alternative_titles'] += ';' +  b_title
        for col in ['directors', 'writers', 'cast', 'genres', 'keywords', 
                    'languages', 'production_companies', 
                    'production_countries']:
            merged.loc[aid, col] = merge_cell(merged.loc[aid, col],
                                              B.loc[bid, col])
        # Rating: take the average after converting B rating to scale 10.
        m_rating = (merged.loc[aid, 'rating'] + 0.1 * B.loc[bid, 'rating']) / 2
        merged.loc[aid, 'rating'] = m_rating
    merged.to_csv(FOLDER+'E.csv', index = True)
    
if __name__ == '__main__':
    main()
