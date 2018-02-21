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

# list directory paths        
MarkedUp = 'stage1_docs/Data/MarkedUp/'
CleanedMarkedUp = 'stage1_docs/Data/Cleaned_MarkedUp/'
DATA = 'stage1_docs/Data/'
def clean_file(filename):
    # remove extra newlines in file
    with open(MarkedUp+filename, encoding = 'utf8') as inputfile:
        oneline_text = ''
        for text in inputfile:
            text = text.rstrip('\n')
            oneline_text = oneline_text + ' ' + text
    cleaned_filename = 'cleaned_' + filename
    with open(CleanedMarkedUp+cleaned_filename, 'w') as outputfile:
        outputfile.write(oneline_text)
    return oneline_text
        
def data_generator(filename, text):
    start_tag = '<pname>'
    end_tag = '</pname>'
    # split text by space
    words_by_space = text.split()
    # split word with 's into 2 separate tokens
    words = []
    split_key = '\'s'
    # split all words that contain split_key
    for word in words_by_space:
        new_word = split_word(word, split_key)
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
                # clean up the word_string
                clean_ws = clean_string(word_string, split_key, start_tag, end_tag)
                print (filename, ',',word_string, ',', clean_ws) 
                # find class label
                class_label = findClassLabel(clean_ws, start_tag, end_tag)
                if class_label == 1:
                    #print (clean_ws)
                    count = count + 1
                # remove markedup tags
                clean_ws = removeTags(clean_ws, start_tag, end_tag)
                # check if words in string all capitalized
                capitalized = isCapitalized(clean_ws)
                # create data instance
                data_instance = [string_id, clean_ws, filename, start, end, capitalized, class_label]
                data.append(data_instance)
                string_id = string_id + 1
                
    print (count)    
    return data       
            
    
    
def split_word(word, split_key):
    # assuming each word has only one split_key
    indices = [i.start() for i in re.finditer(split_key, word)]
    if len(indices) == 0:
        return [word]
    elif len(indices) == 1:
        word1 = word[:indices[0]]
        word2 = word[indices[0]:]
        return [word1, word2]

def clean_string(word_string, split_key, start_tag, end_tag):
    '''
    Clean up punctuations that go before and/or after each string
    only do this for len(word_string) >= 2
    special cases: do not remove punctuations that belong to split_key, start_tag, and end_tag  
    TODO: handle cases like
    *<pname>Kevin Winter</pname>/Getty, or
    *<pname>George R. R. Martin</pname> --> right now the '.' in 'R.' is removed.
    *some cases have weird apostrophe symbols that are not recognized
    as string punctuations: <pname>Scott Cooper</pname>’s
    *sorts.<pname>Bale</pname> -> no white space
    '''
    
    
    if len(word_string) < 2:
        return word_string
    else:
        # get a list of punctuations
        punctuations = string.punctuation
        # get first and last character in the string
        first = word_string[0]
        last = word_string[-1]
        # get index of special words
        start_tag_id = word_string.find(start_tag)
        end_tag_id = word_string.find(end_tag)
        # if first and last are not punctuations no need to clean
        if first not in punctuations and last not in punctuations:
            return word_string
        # if word_string is split_key, no need to clean
        elif word_string == split_key:
            return word_string
        # if first and/or last is a punctuation , check for special cases
        elif first in punctuations and last not in punctuations:
            # if start_tag is at the beginning of word_string, return word_string
            if start_tag_id == 0:
                return word_string
            # remove first from word_string, clean word_string again
            else:
                word_string = word_string[1:]
                return clean_string(word_string, split_key, start_tag, end_tag)
        elif first not in punctuations and last in punctuations:
            #print (word_string)
            # remove last if word_string does not contain end_tag and clean word_string again
            if end_tag_id == -1:
                word_string = word_string[:-1]
                return clean_string(word_string, split_key, start_tag, end_tag)
            # if word_string contains end_tag
            else:
                # if word_string ends with end_tag, return word_string
                if word_string[end_tag_id:] == end_tag:
                    return word_string
                # if word_string does not end with end_tag, remove last, clean string again
                else:
                    word_string = word_string[:-1]
                    return clean_string(word_string, split_key, start_tag, end_tag)
        # if first and last are both punctuations, check for special cases before removing them
        else:
            #print (word_string)
            # if word_string does not start with or have start_tag
            #and does not have end_tag or does not end with an end_tag,
            #remove first and last, clean string again
            if start_tag_id != 0 and (end_tag_id == -1 or
                                      (end_tag_id > 0 and
                                         word_string[end_tag_id:] != end_tag)):
                word_string = word_string[1:-1]
                return clean_string(word_string, split_key, start_tag, end_tag)
            # if word_string does not start with start_tag but ends with end_tag, remove first, clean string again
            elif start_tag_id != 0 and (end_tag_id > 0 and
                                       word_string[end_tag_id:] == end_tag):
                word_string = word_string[1:]
                return clean_string(word_string, split_key, start_tag, end_tag)
            # if word_string starts with start_tag and does not have end_tag,
            # or end_tag is not at the end of the string, remove last, clean string again
            elif start_tag_id == 0 and (end_tag_id == -1 or
                                        (end_tag_id > 0 and
                                         word_string[end_tag_id:] != end_tag)):
                word_string = word_string[0:-1]
                return clean_string(word_string, split_key, start_tag, end_tag)
            # if word_string starts with start_tag and end with end_tag, return string
            elif start_tag_id == 0 and (end_tag_id > 0 and
                                        word_string[end_tag_id:] == end_tag):
                return word_string
                
def isCapitalized(word_string):
    #print (word_string)
    # check if the first letter in each word of a string is capitalized
    word_string = word_string.split()
    flag = 1 # capitalized
    for word in word_string:
        if not word[0].isupper:
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
    
    
def findClassLabel(word_string, start_tag, end_tag):
    # find the class label for the word_string
    class_label = 0 # negative label
    start_tag_id = word_string.find(start_tag)
    end_tag_id = word_string.find(end_tag)
    if start_tag_id == 0 and end_tag_id > 0 and word_string[end_tag_id:] == end_tag:
        class_label = 1 # positive label
    return class_label

# test clean_file
#online_text = clean_file('19_m.txt')
#print (online_text)
#data = data_generator('19_m.txt', online_text)
#write_to_file(data, 'data.csv')    
    
def main():
    csv_file = DATA + 'data.csv'
    headers = ['string_id', 'string', 'document_id', 'start_index', 'end_index', 'capitalized', 'class_label']
    # open MarkedUp folder and process all files
    for filename in os.listdir(MarkedUp):
        if os.path.isfile(filename) == False:
            text = clean_file(filename)
            data = data_generator(filename, text)
            df = pd.DataFrame(data, columns = headers)
            # if csv_file is already exist, open it and append new data
            if os.path.isfile(csv_file) == True:
                df.to_csv(csv_file, mode = 'a', header = False)
            else:
                df.to_csv(csv_file, header = True)
                
if __name__ == "__main__":
    main()
