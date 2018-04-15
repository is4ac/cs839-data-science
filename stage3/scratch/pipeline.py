import py_entitymatching as em

def main():
    A = em.read_csv_metadata('../Data/A_imdb.csv', key='id')
    B = em.read_csv_metadata('../Data/B_tmdb.csv', key='id')
    ab = em.AttrEquivalenceBlocker()
    shared_attributes = ['title', 'directors', 'release_year', 'languages']
    C = ab.block_tables(A, B, 'directors', 'directors', 
                        l_output_attrs=shared_attributes,
                        r_output_attrs=shared_attributes)
    # Take a sample of 10 pairs
    S = em.sample_table(C, 100)
    print(S)
    G = em.label_table(S, label_column_name='gold_labels')
    train_test = em.split_train_test(G, train_proportion=0.5)
    train, test = train_test['train'], train_test['test']
    # Get feature for matching
    match_f = em.get_features_for_matching(A, B)
    H = em.extract_feature_vecs(train,
                                attrs_before=['ltable_title', 'rtable_title'],
                                feature_table=match_f,
                                attrs_after=['gold_labels'])
    H.fillna(value=0, inplace=True)
    print(H)
    # Specifying Matchers and Performing Matching.
    dt = em.DTMatcher(max_depth=5)  # A decision tree matcher.
    # Train the matcher
    dt.fit(table=H,
           exclude_attrs=['_id', 'ltable_id', 'rtable_id', 'ltable_title',
                          'rtable_title', 'gold_labels'], 
           target_attr='gold_labels')
    # Predict
    F = em.extract_feature_vecs(test,
                                attrs_before=['ltable_title', 'rtable_title'],
                                feature_table=match_f,
                                attrs_after=['gold_labels'])
    F.fillna(value=0, inplace=True)
    print(F)
    pred_table = dt.predict(
        table=F,
        exclude_attrs=['_id', 'ltable_id', 'rtable_id', 'ltable_title', 
                       'rtable_title', 'gold_labels'],
        target_attr='predicted_labels', return_probs=True, 
        probs_attr='proba', append=True, inplace=True)
    print(pred_table)
    eval_summary = em.eval_matches(pred_table, 'gold_labels', 'predicted_labels')
    em.print_eval_summary(eval_summary)

    # Now apply to the entire pairs
    
    # Now just select matchers
    #dt = em.DTMatcher()
    #rf = em.RFMatcher()
    #result = em.select_matcher(matchers=[dt, rf], table=train, 
    #                           exclude_attrs=['_id', 'ltable_id', 'rtable_id', 'ltable_title', 
    #                                          'rtable_title'],
    #                           target_attr='gold_labels', k=5)
    print(result)

if __name__ == '__main__':
    main()
