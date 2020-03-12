# -*- coding: utf-8 -*-
"""
Paul Khawaja
INLS570
Project Phase 2 - Query Interface
"""
import re
import math

#------------File Extraction----------------------#
def getStopWords():
    """reads stopwords.txt to get the stop words to exclude.
    ----------
    Returns:
    stop_words (list): list of all stop words from stopwords.txt
    """
    stop_words = []
    stop_file = open("stopwords.txt", "r")
    for line in stop_file:
        line = line.strip()
        stop_words.append(line)
    stop_file.close()
    
    return stop_words
 

def getGrimmText():
    """reads grimms.txt to get the lines of Grimms' Fairy Tales (GFT)
    ----------
    Returns:
    grimms_lines (list): list of all story lines from GFT
    """
    grimms_file = open("grimms.txt", "r")
    # create the list of lines stripping the parts we don't need
    for line in grimms_file:
        grimms_lines = grimms_file.readlines()[123:9180] 
    grimms_file.close()
    
    return grimms_lines

#------------Index Creation----------------------#
def storyToWords(stop_words, grimms_lines):
    """Creates a dictionary of words in Grimms' Fairy Tales (GFT)
    ----------
    Parameters:
    stop_words (list): The list of stop words to exclude from the dictionary
    story_lines (list): The lines extracted from grimms.txt 
    ----------
    Returns:
    search_index (dict): A dict where each key is a word from GFT each value is
    a dict where its key is a story title and its value is a list of line 
    numbers where the word appears. 
    """
    line_number = 125 # the stories start at line 125
    search_index = {}
    for item in grimms_lines:
        # skip if it's blank 
        if re.match(r'\s', item):
                pass
        # if it's a story title, store it in a variable. 
        elif re.match(r'^[A-Z]+([ -]?[A-Z]+)*\n$', item):
                story = item.strip()
        # if it's a line of a story, get the words and add to index
        else: 
            # remove punctuation, then extra spaces, then make lowercase
            clean_text = re.sub(r'[^\w\s]',' ',item).strip().lower()
            sentence = clean_text.split() #split sentences into words
            for word in sentence:
                # skip if stop word
                if word in stop_words:
                    pass
                # the word is not yet in the index - create word and story
                elif word not in search_index:
                    search_index.update({word:{story:[line_number]}})
                else:
                    # first check if the story is there. 
                    if story in search_index[word]:
                        search_index[word][story].append(line_number)  
                    # if no story, add the story
                    else: 
                        search_index[word].update({story:[line_number]})
        line_number += 1 
        
    return search_index

#------------Running Queries----------------------#
def makeQuery(search_index, grimms_lines):
    """Starts the query search interface to find words in the grimms text.
    ----------
    Parameters:
    search_index (dict): the dict returned from storyToWords(...)
    grimms_lines (list): the list returned from getGrimmText()
    ----------
    This function does not return until the user types 'qquit', 
    otherwise, it continues to call itself and run other
    query functions. 
    """
    user_input = input("Please enter your query: ")
    query = user_input.lower().split()
    print('\nquery = ' + user_input ) # print out the query
    # quit the interface
    if len(query) == 1 and query[0] == "qquit": 
        return print("Exiting the search interface, goodbye.")
    # re-print the instructions/commands
    elif len(query) == 1 and query[0] == "hhelp":
        getInstructions()
        makeQuery(search_index, grimms_lines)
    elif len(query) == 1:
        print(singleWordQuery(query[0], search_index, grimms_lines))
        makeQuery(search_index, grimms_lines)
    # morethan query
    elif len(query) == 3 and query[1] == 'morethan': 
        print(moreThanQuery(query[0], query[2], search_index, grimms_lines))
        makeQuery(search_index, grimms_lines)
    # OR queries
    elif len(query) == 3 and query[1] == 'or':
        print(orQuery(query[0],query[2], search_index, grimms_lines))
        makeQuery(search_index, grimms_lines)
    # AND queries
    else:  
        andQuery(query,search_index, grimms_lines)
        makeQuery(search_index, grimms_lines)
        

def singleWordQuery(word, search_index, grimms_lines):
    """Takes a single word and finds all instances of it in the Grimms' index.
    Also sorts the results based on each story's TF.IDF score for the word. 
    ----------
    Parameters: 
    word (string): the user input of the word to query the index for
    search_index (dict): the dict returned from storyToWords(...)
    grimms_lines (list): the list returned from getGrimmText()
    ----------
    Prints results with the general format:    
    <STORY TITLE 1> <TD.IDF SCORE>
        <line_num> <sentence>
        <line_num> <sentence>
        ...
    <STORY TITLE 2> <TD.IDF SCORE>
        ...
      <line_num> <sentence>
    """
    word_dict = search_index.setdefault(word, {})
    # if it's empty, just print --
    if len(word_dict) == 0: 
        return print('\t --')
    # if not empty, get add tf.idf values to keys
    word_tfIDF = tfIDF(word,word_dict)
    # reformat the dictionary
    single_dict = {key:{word:val} for key,val in word_tfIDF.items()}
    # start printing dictionary query
    sorted_keys = sorted(single_dict,key=sortByTFIDF,reverse=True)
    for title in sorted_keys:
        print('\t' + title)
        word_lines = single_dict[title] # gets the {word: [lines]} for story
        for term, line_nums in word_lines.items():
            if type(line_nums) == list:
                # print for each line number where the word appears
                for num in line_nums:
                    line = '\t    ' + str(num) + ' ' + grimms_lines[num - 125]
                    emphasis = line.replace(word, '**' + word.upper() + '**')
                    print(emphasis, end='')
            # if that word has no lines in this story, print --
            else:
                print('\t    --')    
        
    
def orQuery(word1, word2, search_index, grimms_lines):
    """Takes two words and finds stories with either words in the grimms index,
    outputting the matching stories and lines of text for both words.
    ----------
    Parameters:
    word1 (string): the first word the users input in the query
    word2 (string): the second word the user input in the query 
    search_index (dict): the dict returned from storyToWords(...)
    grimms_lines (list): the list returned from getGrimmText()
    ----------
    Returns:
    printQuery(...) (function/None): the function to print the OR query
    """
    # get sub dictionaries for each word. If word not present, make empty dict
    word1_dict = search_index.setdefault(word1, {})
    word2_dict = search_index.setdefault(word2, {})
    # reformat the dictionaries 
    reform_dict1 = {key:{word1:val} for key,val in word1_dict.items()}
    reform_dict2 = {key:{word2:val} for key,val in word2_dict.items()}
    # merge the dictionaries using mergeDict(...)
    or_dict = mergeDict(word1, word2, reform_dict1, reform_dict2)
    
    return printQuery(or_dict, grimms_lines)


def andQuery(query, search_index, grimms_lines):
    """Takes a list of words and finds stories with all words in the grimms 
    index, outputting the matching stories and lines of text. 
    ----------
    Parameters:
    query (list): the words in the query
    search_index (dict): the dict returned from storyToWords(...)
    grimms_lines (list): the list returned from getGrimmText()
    ----------
    Returns:
    printQuery(...) (function/None): the function to print the query
    """
    #remove and from query if it's present
    if 'and' in query: query.remove('and') 
    word_Dicts = []
    i = 1
    # get queries of each individual word and format them
    for word in query:
        word_dict = search_index.setdefault(word, {})
        reform_dict = {key:{word:val} for key,val in word_dict.items()}
        word_Dicts.append(reform_dict)
    # start building the multiple word dictionary
    and_dict = mergeDict(query[0], query[1], word_Dicts[0], word_Dicts[1])
    # loop through remaining words merging them into the dictionary
    if len(query) > 2:
        for word_dict in word_Dicts[2:]:
            and_dict = mergeDict(query[i], query[i + 1], and_dict, word_Dicts[i+1])
            i += 1
        # add terms from the query list to stories where they are missing
        for story, term in and_dict.items():
            for word in query:
                if word not in term:
                    term[word] = ''
    # delete any stories with empty values
    for story in [story for story, word in and_dict.items() 
    if any(x == '' for x in list(word.values()))]: 
        del and_dict[story]
        
    return printQuery(and_dict, grimms_lines)


def moreThanQuery(word1, compare, search_index, grimms_lines):
    """Takes a word and a word or number to compare to and returns
    stories where the word appears in more times than the other word or number.
    ----------
    Parameters:
    word1 (string): the word from the query
    compare (string): the word or number to compare word1 to
    search_index (dict): the dict returned from storyToWords(...)
    grimms_lines (list): the list returned from getGrimmText()
    """
    word1_dict = search_index.setdefault(word1, {})
    more_dict = {key:{word1:val} for key,val in word1_dict.items()}
    # first check if compare is a number or another word
    if compare.isdigit(): 
        # delete stories < compare
        for story in [story for story, word in more_dict.items() 
        if any(len(x) <= int(compare) for x in list(word.values()))]: 
            del more_dict[story]
        # print the dict
        
        return printQuery(more_dict, grimms_lines)
    
    # if we are comparing two words    
    else: 
        word2_dict = search_index.setdefault(compare, {})
        compare_dict = {key:{compare:val} for key,val in word2_dict.items()}
        morethan = mergeDict(word1, compare, more_dict, compare_dict)
        # delete stories where word 1 < word 2
        for story in [story for story, word in morethan.items()
        if (len(word[word1]) <= len(word[compare]))]:
            del morethan[story]
            
        return printQuery(morethan, grimms_lines)
        

#------------Help Functions for Queries----------------------#
def mergeDict(word1, word2, word1_dict, word2_dict):
    """Merges two dictionaries to reformat them for printing out the
    query results. 
    ----------
    Parameters:
    word1 (string): the first word the users input in the query
    word2 (string): the second word the user input in the query 
    word1_dict (dict): the sub dictionary from querying word1
    word2_dict (list): the sub dictionary from querying word2
    ----------
    Returns:
    merged_dict (dict): a merged and formatted dictionary of word1_dict and
    word2_dict, for printing in the desired query format. 
    """
    # make a copy of dict1 do do merge with dict2 into 
    merged_dict = word1_dict.copy()
    # merge content of both dictionaries into merged_dict
    for story, term in word2_dict.items():
        if story in word1_dict: # if the same story is in both
            merged_dict[story][word2] = word2_dict[story][word2]
        else: # not in dict1 but in dict2
            merged_dict[story] = term
    # if a word does not appear in a story, give it an empty value
    for story, term in merged_dict.items():
        if word1 not in term:
            term[word1] = ''
        if word2 not in term:
            term[word2] = ''
            
    return merged_dict

            
def printQuery(query_dict, grimms_lines):
    """Takes a dictionary created by a query search and prints it out
    ----------
    Parameters:
    query_dict (dict): the dictionary of words and stories from a query
    grimms_lines (list):
    ----------
    Prints results with the general format:    
    <STORY TITLE 1>
      <word1>
        <line_num> <sentence>
        <line_num> <sentence>
        ...
      <word2>
        -- 
    <STORY TITLE 2> 
      <word1>
        --
    <word2>
      <line_num> <sentence>
    """
    if len(query_dict) == 0:
        return print('\t --')
    # if at least one is in the dict, print out the results
    for story, words in query_dict.items():
        print('\t' + story)
        # go through sub dictionary of words and line numbers
        for word, line_nums in words.items():
            print('\t  ' + word)
            # if there are line numbers for that word, print them out
            if type(line_nums) == list: 
                # print for each line number where the word appears
                for num in line_nums:   
                    line = '\t    ' + str(num) + ' ' + grimms_lines[num - 125]
                    emphasis = line.replace(word, '**' + word.upper() + '**')
                    print(emphasis, end='')
            # if that word has no lines in this story, print --
            else:
                print('\t    --')
                

def tfIDF(word, word_dict):
    """Takes a word and the dictionary from the search index query from that
    word and returns a new word dictionary formatted with TF.IDF scores for
    each chapter. 
    ----------
    Parameters: 
    word (string): the queried word
    word_dict (dict): the dictionary produced by the query
    ----------
    Returns: 
    tfidf_dict (dict): the word_dict modified to include TF.IDF scores in
    the keys 
    """
    IDF = math.log(64/len(word_dict), 2)
    tfidf_dict = {}
    for key, val in word_dict.items():
        tf_idf = round(len(val) * IDF, 3)
        new_key = key + ' (TF*IDF = ' + str(tf_idf) + ')'
        tfidf_dict[new_key] = val
        
    return tfidf_dict
        
    
def sortByTFIDF(item):
    '''takes a key formatted by tfIDF(...) and strips all non-digits
    to get just the TF.IDF score. uses that score as a float to sort
    the results
    ----------
    Parameters:
    item (string): a string that is a key in a word dictionary
    ----------
    Returns:
    tf_idf (float): the tf_idf score extracted from the item
    '''
    tf_idf = float(re.sub(r'[^0-9.]','',item))
    
    return tf_idf
        
            
def getInstructions():
    """Prints out the available commands of the query interface.
    """
    print('''Welcome to the Grimms' Fairy Tales Search Interface!
    You can search using the following commands: \n
    DESCRIPTION --- COMMAND1|COMMAND2|...
    --------------------------------------------------------
    Stories with Single Word --- word1
    Stories containing word1 or word2 --- word1 or word2
    Stories containing word1 and word2 --- word1 word2 | word1 and word2
    Stories containing n words --- word1 word2 word3 . . . wordn
    Stories where word1 occurs more than x times --- word1 morethan x
    Stories where word1 occurs more than word2 --- word1 morethan word2 \n
    To quit the program ---qquit
    To print commands again --- hhelp''')
   
    
#------------Main----------------------#
def main():
    stop_words = getStopWords()
    grimms = getGrimmText() 
    s2w = storyToWords(stop_words, grimms)   
    getInstructions()
    makeQuery(s2w, grimms)
    
if __name__ == '__main__':
    main()
