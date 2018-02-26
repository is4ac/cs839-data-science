# -*- coding: utf-8 -*-
__author__ = 'Trang Vu'
'''
    inputs: marked up '.txt' files
    outputs: a csv file with each entry correspond to a string, which has the following fields:
        string id: integer
        the string of either 1, 2, 3, or 4 consecutive words: string 
        file id/file name: string 
        start position of the string: integer
        end position of the string: integer
        capitalized: binary with 1 or 0 being all first letters are or are not capitalized respectively 
        class label: binary with 1  or 0 being the string is or is not a person name, respectively 
'''        

# load packages
import os
import string
import re
import pandas as pd
import random

# list directory paths        
MarkedUp = 'stage1_docs/Data/MarkedUp/'
CleanedMarkedUp = 'stage1_docs/Data/Cleaned_MarkedUp/'
DATA = 'stage1_docs/Data/'

# Global feature names that will be shared between modules
LOCATION_FEATURES = ['document_id', 'start_index', 'end_index']
OTHER_FEATURES = ['capitalized', 'prefixed', 'suffixed', 'otherEntity']
TRAIN_CSV = DATA + 'train_data.csv'
TEST_CSV = DATA + 'test_data.csv'

def clean_file(filename):
    # remove extra newlines in file
    # replace weird apostrophe by single quote
    # check if number of end_tags == number of star_tags
    with open(MarkedUp+filename, encoding = 'utf8') as inputfile:
        oneline_text = ''
        for text in inputfile:
            text = text.rstrip('\n')
            text = text.replace('’', '\'')
            oneline_text = oneline_text + ' ' + text
    start_tag = '<pname>'
    end_tag = '</pname>'
    num_start_tag = len([i.start() for i in re.finditer(start_tag, oneline_text)])
    num_end_tag = len([i.start() for i in re.finditer(end_tag, oneline_text)])
    if num_start_tag != num_end_tag:
        print ('Tags are mismatched! Check markedup file: ' + filename)
    else:
        cleaned_filename = 'cleaned_' + filename
        with open(CleanedMarkedUp+cleaned_filename, 'w') as outputfile:
            outputfile.write(oneline_text)
    return oneline_text
        
def data_generator(filename, text):
    start_tag = '<pname>'
    end_tag = '</pname>'
    # split text by space
    words_by_space = text.split()
    # split words further by punctuations
    words = []
    for word in words_by_space:
        new_word = split_string(word)
        words.extend(new_word) 
    # generate list of strings of words
    data = []
    string_id = 0
    count = 0
    for index in range(0, len(words)):
        for num_words in range(1, 5):
            if index + num_words <= len(words): 
                word_string = words[index:index+num_words]
                word_string = ' '.join(word_string)
                #print (word_string)
                start = index
                end = index + num_words
                # check if preceding word is a special prefix
                prefix = 0
                if start > 0:
                    prefix = checkPrefix(words[start - 1])
                # check if succeding word is a special suffix
                suffix = 0
                if end < len(words):
                    suffix = checkSuffix(words[end])
                otherEntity = 0
                if start > 0 and end < len(words):
                    otherEntity = checkOthers(words, start - 1, end)
                # find class label
                class_label = findClassLabel(word_string, start_tag, end_tag)
                if class_label == 1:
                    count = count + 1
                # remove markedup tags
                word_string = removeTags(word_string, start_tag, end_tag)
                # check if words in string all capitalized
                capitalized = isCapitalized(word_string)
                # create data instance
                data_instance = [string_id, word_string, filename, start, end, capitalized, prefix, suffix, otherEntity, class_label]
                data.append(data_instance)
                string_id = string_id + 1
    return data       
    
def split_string(word_string):
    '''
    Split string into words and punctuations except for string with tags and
    special words. Return a list of string
    '''
    start_tag = '<pname>'
    end_tag = '</pname>'
    title_words = ['Dr.', 'Esq.', 'Hon.', 'Jr.', 'Mr.', 'Mrs.', 'Ms.', 'Messrs.',
                   'Mmes.', 'Msgr.', 'Prof.', 'Rev.', 'Rt. Hon.', 'Sr.', 'St.']
    specials = ['U.S.'] # can extend this list
    start_tag_id = word_string.find(start_tag)
    end_tag_id = word_string.find(end_tag)
    split_words = []
    # if word_string only has 1 character, return it
    if len(word_string) < 2:
        split_words.append(word_string)
        return split_words
    # if word_string is all alphabets, or all digits, or can be convert to a float, or alphanumeric, return it
    elif word_string.isalpha() or word_string.isdigit() or word_string.isalnum() or isNumber(word_string):
        split_words.append(word_string)
        return split_words
    # if word_string starts or ends with tags, return it
    elif start_tag_id == 0:
        if word_string[end_tag_id:] == end_tag:
            split_words.append(word_string)
            return split_words
        elif end_tag_id > 0 and word_string[end_tag_id:] != end_tag:
            split_pos = end_tag_id + len(end_tag)
            word1 = word_string[:split_pos]
            word2 = word_string[split_pos:]
            split_word2 = split_string(word2)
            split_word2.insert(0, word1)
            return split_word2
        elif end_tag_id == -1:
            split_words.append(word_string)
            return split_words
    # if word_string has start_tag but it does not start with start_tag, split it
    elif start_tag_id > 0:
        word1 = word_string[0:start_tag_id]
        word2 = word_string[start_tag_id:]
        split_word1 = split_string(word1)
        split_word2 = split_string(word2)
        split_word1.extend(split_word2)
        return split_word1
    elif start_tag_id == -1:
        if word_string[end_tag_id:] == end_tag:
            split_words.append(word_string)
            return split_words
        elif end_tag_id > 0 and word_string[end_tag_id:] != end_tag:
            split_pos = end_tag_id + len(end_tag)
            word1 = word_string[:split_pos]
            word2 = word_string[split_pos:]
            split_word2 = split_string(word2)
            split_word2.insert(0, word1)
            return split_word2
        elif end_tag_id == -1:
            # if word_string is not alphanumeric, split it
            # find first position that is not alphanumeric
            first_nonalnum = find_first_nonalnum(word_string)
            # if first_nonalnum character is a period, make sure it's not part of title words or initials
            if word_string[first_nonalnum] == '.':
                if word_string in title_words:
                    split_words.insert(0, word_string)
                    return split_words
                elif len(word_string) == 2 and word_string[0].isupper():
                    split_words.insert(0, word_string)
                    return split_words
                elif word_string in specials:
                    split_words.insert(0, word_string)
                    return split_words
                else:
                    word1 = word_string[0:first_nonalnum]
                    word2 = word_string[first_nonalnum]
                    word3 = word_string[first_nonalnum+1:]
                    if len(word1) > 0:
                        split_word1 = split_string(word1)
                    else:
                        split_word1 = word1
                    if len(word3) > 0:
                        split_word3 = split_string(word3)
                    else:
                        split_word3 = word3
                    if len(split_word1) > 0:
                        split_word1.append(word2)
                        if len(split_word3) > 0:
                            split_word1.extend(split_word3)
                        return split_word1
                    else:
                        if len(split_word3) > 0:
                            split_word3.insert(0, word2)    
                            return split_word3
            # if first_nonalnum character is an apostrophe, make sure it's not part of the 's
            elif word_string[first_nonalnum] == '\'':
                if len(word_string) == 2 and word_string[-1] == 's':
                    split_words.append(word_string)
                    return split_words
                elif len(word_string) > 2 and word_string[-1] == 's':
                    word1 = word_string[0:first_nonalnum]
                    word2 = word_string[first_nonalnum:]
                    split_words.append(word1)
                    split_words.append(word2)
                    return split_words
                else:
                    split_words.append(word_string)
                    return split_words
            else:            
                word1 = word_string[0:first_nonalnum]
                word2 = word_string[first_nonalnum]
                word3 = word_string[first_nonalnum+1:]
                if len(word1) > 0:
                    split_word1 = split_string(word1)
                else:
                    split_word1 = word1
                if len(word3) > 0:
                    split_word3 = split_string(word3)
                else:
                    split_word3 = word3
                if len(split_word1) > 0:
                    split_word1.append(word2)
                    if len(split_word3) > 0:
                        split_word1.extend(split_word3)
                    return split_word1
                else:
                    if len(split_word3) > 0:
                        split_word3.insert(0, word2)    
                        return split_word3

def find_first_nonalnum(word):
    for char in word:
        if not char.isalnum():
            return(word.index(char))

def isNumber(word):
    try:
        float(word)
        return True
    except ValueError:
        return False

def isCapitalized(word_string):
    #print (word_string)
    # check if the first letter in each word of a string is capitalized
    word_string = word_string.split()
    flag = 1 # capitalized
    for word in word_string:
        if not word[0].isupper():
            flag = 0 # not capitalized
            break
    return flag
            
def removeTags(word_string, start_tag, end_tag):
    # remove markedup tags
    if start_tag in word_string:
        word_string = word_string.replace(start_tag, '')
    if end_tag in word_string:
        word_string = word_string.replace(end_tag, '')
    return word_string

def checkPrefix(word):
    # check if word_string has a title
    prefixes = ['Dr.', 'Esq.', 'Hon.', 'Jr.', 'Mr.', 'Mrs.', 'Ms.', 'Prof.', 'Rev.',
                'Sr.', 'St.', 'Dr', 'Esq', 'Hon', 'Jr', 'Mr', 'Mrs', 'Ms', 'Prof', 'Rev',
                'Sr', 'St', 'Lady', 'Lord', 'Captain', 'President', 'General', 'Doctor', 'Professor',
                'Father', 'Reverend', 'Earl', 'Mister', 'Miss', 'Madam', 'Chancellor',
                'Vice-President', 'Dean', 'Pope', 'Rabbi', 'Prince', 'Queen', 'Princess',
                'director', 'composer', 'actor', 'actress', 'chief', 'detective', 'screenwriter',
                'producer']
    if word in prefixes:
        return 1
    else:
        return 0

def checkSuffix(word):
    # check if word_string followed by 
    verbs = ['says', 'said', 'talk', 'talked', 'writes', 'wrote', 'plays', 'played',
             'believes', 'believed', 'explains', 'explained', '\'s', 'who', 'starred']
    if word in verbs:
        return 1
    else:
        return 0
        
def checkOthers(words, before_index, after_index):
    # check if word_string maybe a location name or movie name
    preceeding_words = ['the', 'The', 'in', 'on', 'at']
    succeeding_words = ['avenue', 'city', 'street', 'st', 'ave', 'town', 'village']
    if words[before_index] in preceeding_words or words[after_index] in succeeding_words:
        return 1
    else:
        return 0

def findClassLabel(word_string, start_tag, end_tag):
    # find the class label for the word_string
    class_label = 0 # negative label
    start_tag_id = word_string.find(start_tag)
    end_tag_id = word_string.find(end_tag)
    if start_tag_id == 0 and end_tag_id > 0 and word_string[end_tag_id:] == end_tag:
        class_label = 1 # positive label
    return class_label

def createDevAndTestFileSet():
    """ Shuffles the marked-up file set and divide it into two for training and testing.
    Returns 'train_file_names' and 'test_file_names'."""
    file_names = []
    for file_name in os.listdir(MarkedUp):
        file_names.append(file_name)
    # shuffle the list, and create training and testing list
    random.shuffle(file_names)
    return file_names[ : int(len(file_names) * 0.66)], file_names[int(len(file_names) * 0.66) : ]

def extractAndCreateCSV(file_names, csv_file):
    """Scan all the files in file_names and produces a single CSV file that
    containing strings, feature vectors, and class_label."""
    global LOCATION_FEATURES
    global OTHER_FEATURES
    headers = ['string_id', 'string'] + LOCATION_FEATURES + OTHER_FEATURES + ['class_label']
    print('creating csv file:' + csv_file)
    # open MarkedUp folder and process all files
    for filename in file_names:
        if os.path.isfile(filename) == False:
            text = clean_file(filename)
            text = text.replace('’', '\'')
            data = data_generator(filename, text)
            df = pd.DataFrame(data, columns = headers)
            # if csv_file is already exist, open it and append new data
            if os.path.isfile(csv_file) == True:
                # check if filename is already processed:
                existing_df = pd.read_csv(csv_file)
                file_list = list(existing_df['document_id'])
                if filename in file_list:
                    print ('Skip file: ', filename)
                    continue
                else:                
                    df.to_csv(csv_file, mode = 'a', encoding = 'utf-8', header = False)
            else:
                df.to_csv(csv_file, encoding = 'utf-8', header = True)

def main():
    global TEST_CSV
    global TRAIN_CSV
    train_input_files, test_input_files = createDevAndTestFileSet()
    print(train_input_files)
    print(test_input_files)
    extractAndCreateCSV(train_input_files, TRAIN_CSV)
    extractAndCreateCSV(test_input_files, TEST_CSV)
                
if __name__ == "__main__":
    main()
