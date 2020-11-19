import pandas as pd
import numpy as np
import re
import xlrd
import matplotlib.pyplot as plt
import seaborn as sns
import traceback
from fuzzywuzzy import fuzz
from nltk.util import ngrams
from itertools import groupby
from math import atan2,degrees
import nltk
import numpy as np
from nltk import sent_tokenize
from nltk.chunk.regexp import *
from nltk.corpus import stopwords

def readCSV(fileName,sheetName):
    try:
        if sheetName!="NA":
            df = pd.read_csv(fileName)
        else:
            df = pd.read_csv(fileName,sheetName)
        # print(df.columns)
        Data=df['Invoice Number,']
        #Data = df['Total,']
        return Data
    except:
        print(traceback.print_exc())
######################################################################################################################################
'''Feature0: Word Length'''
def attribute_length(word):
    word = str(word)
    try:
        return len(word) #returns the length of the attribute
    except:
        return '-1'
######################################################################################################################################
'''Feature1: Word Format'''

def attribute_type(orgword):
    try:
        #print('I m here')
        word = orgword.replace(',','')
        #print(word)
        if re.match('^[0-9.,/ \\\()\-]+$', word): #check if numeric
            return 1
        elif re.match('^[A-Za-z.,:/\- \\\()]+$', word): #check if alphabets
            return 2
        elif re.match('^[A-Za-z0-9.,:/\- \\\()]+$', word): # check if alphanumeric
           return 3
        elif re.match('^[\$\£\Rs\Rs.]{1}[\d,]+\.?\d{0,2}',word): # check for amount
            print('####### in return 4')
        # elif re.match('^[\A-Z][\$\£]{1}[\d,]+\.?\d{0,2}',word):
        #elif re.match('^\$\A?([0-9]{1,3},([0-9]{3},)*[0-9]{3}|[0-9]+)(.[0-9][0-9])?$',word):
            return 4
        else:
            return 0
    except:
        return -1   


######################################################################################################################################
'''Feature2: Presence of special symbols or characters in the words'''
def attribute_symbol(word):
    # print('I m in symbol')
    # print(type(word))
    try:
        return_symbol = []

        if "." in word and "," in word:  # check if contains dot and comma
            # print('I m in 1')
            return_symbol.append(1)
        ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

        if not return_symbol:

            if "-" in word and "/" in word:  # check if contains dash and slash
                return_symbol.append(2)
            ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            if not return_symbol:

                if "-" in word and "," in word:  # check if contains dash and slash
                    return_symbol.append(3)
                ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
                if not return_symbol:

                    if "." in word: #check if contains dot
                        return_symbol.append(4)
                    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
                    if "-" in word: #check if contains dash
                        return_symbol.append(5)
                    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
                    if "/" in word: #check if contains slash
                        return_symbol.append(6)
                    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
                    if "," in word: #check if contains comma
                        return_symbol.append(7)
                    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
                    if "\\" in word: #check if contains backslash
                        return_symbol.append(8)
                    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
                    if ":" in word:  # check if contains colon
                        return_symbol.append(9)
                    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
                    if ";" in word:  # check if contains semi colon
                        return_symbol.append(10)
                    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

        if len(return_symbol) == 0:
            return 0
        else:
            return_symbol = [str(i) for i in return_symbol]
            return ''.join(return_symbol)
            #return
    except Exception as e:
        print(e)
        return -1
######################################################################################################################################
'''Feature3 and Feature5: Word-level Distribution'''
def attribute_distribution(word):
    try:
        return_distribution = []

        if word.isupper() or re.match('^[0-9.,/ \\\()\-]+$', word) or re.match('^[\$\£]{1}[\d,]+\.?\d{0,2}',word): # check if all capital letters or numeric or amount
            return_distribution.append(1)
        ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        if not return_distribution:
            word=re.findall(r'[A-Za-z]',word)
            word = "".join(word)
            if word:
                if word[0].isupper(): # check if starts with capital letter
                    return_distribution.append(2)
        if word:
            if word.islower():
            # if re.match('^[a-z]', word):
                return_distribution.append(3) # check if all small letters
            if not return_distribution:
                if word[0].islower():  # check if starts with small letter
                    return_distribution.append(4)
        ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

        if len(return_distribution) == 0:

            return 0
        else:
            return_distribution = [str(i) for i in return_distribution]
            return ''.join(return_distribution)
    except Exception as e:
        print(e)
        return -1
######################################################################################################################################
'''Feature4: Checking the type for first and last characters'''
def startendchar(word):
    try:
        return_startendchar = []
        if re.match('^[A-Za-z]', word[0]) and re.match('^[A-za-z]', word[-1]): # check if start character is alphabet and end character is also alphabet
            return_startendchar.append(1)
        ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        if re.match('^[0-9]', word[0]) and re.match('^[0-9]', word[-1]): # check if start character is numeric and end character is also numeric
            return_startendchar.append(2)
        ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        if re.match('^[A-za-z]', word[0]) and re.match('^[0-9]', word[-1]): # check if start character is alphabet and end character is numeric
            return_startendchar.append(3)
        ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        if re.match('^[0-9]', word[0]) and re.match('^[A-za-z]', word[-1]): # check if start character is numeric and end character is alphabet
            return_startendchar.append(4)
        ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        if re.match('^[\$\£]', word[0]) and re.match('^[0-9]', word[-1]): # check if start charcter is symbol and end character is numeric
            return_startendchar.append(5)
        if len(return_startendchar) == 0:
            return 0
        else:
            return_startendchar = [str(i) for i in return_startendchar]
            return ''.join(return_startendchar)
    except:
        return -1

######################################################################################################################################

'''Feature5: Checking for the word-level pattern'''
def wordpattern(orgword):
    try:
        word = orgword.replace(',','')
        if re.match(r'^[a-zA-Z]{5}[0-9]{4}[a-zA-Z]$', re.sub(r'\s+', '',word)): # check for panno pattern
            return 1

    except:
        return -1


######################################################################################################################################
'''Supporting Feature:Finding the data pattern'''
def dataarrangement(word):
    try:
        datapattern=[]
        for element in range(0, len(word)):
            if word[element].isalpha():  #check if character is alphabetic
                datapattern.append(1)
            if word[element].isnumeric():  # check if character is numeric
                datapattern.append(2)
            # if word[element] == '-' or word[element] == '.' or word[element] == '/' or word[element] == ',' or word[element] == ':'\
            #     or word[element] == '&' or word[element] == '%' or word[element] == '@' or word[element] == '$' or\
            #     word[element] == '¥' or word[element] == '₹' or word[element] == ';' or word[element] == '}'or word[element] == '|':  # check if character is some special symbols
            else:
                datapattern.append(3)
        datapattern = [str(i) for i in datapattern]
        #print(datapattern)
        output = [(key, len(list(group))) for key, group in groupby(datapattern)]
        #print(output)
        return output,datapattern
    except:
        print("Problem in getWordcoordinate",traceback.print_exc())
        return -1

#####################################################################################################################################
'''Feature5: Getting the prefix word type'''

def getprefix_type(word):
    # print(word)
    output, _ = dataarrangement(word)
    n_prefix_type = output[0][0]
    prefix_type = []
    if n_prefix_type == '1':
        prefix_type.append(1)
    elif n_prefix_type == '2':
        prefix_type.append(2)
    elif n_prefix_type == '3':
        prefix_type.append(3)
    else:
        prefix_type.append(0)
    return prefix_type[0]

#####################################################################################################################################
''' Feature7: Getting the prefix_word'''
def getprefix(word):
    _gramfeatures=[]
    output, _ = dataarrangement(word)
    n_prefix = output[0][1]
    prefixword = word[:n_prefix]
    _gramfeaturesprefix=[prefixword[i:i + n_prefix] for i in range(len(prefixword) -n_prefix + 1)] #Finding n-gram features
    return _gramfeaturesprefix[0]

#####################################################################################################################################
''' Feature6: Getting the suffix word type'''
def getsufix_type(word):
    output, _ = dataarrangement(word)
    n_suffix_type = output[-1][0]
    suffix_type = []
    if n_suffix_type == '1':
        suffix_type.append(1)
    elif n_suffix_type == '2':
        suffix_type.append(2)
    elif n_suffix_type == '3':
        suffix_type.append(3)
    else:
        suffix_type.append(0)
    return suffix_type[0]
######################################################################################################################################
''' Feature8: Getting the suffix_word'''
def getsuffix(word):
    output, _ = dataarrangement(word)
    n_suffix = output[-1][1]
    suffixword = word[-n_suffix:]
    _gramfeaturessuffix = [suffixword[i:i + n_suffix] for i in range(len(suffixword) - n_suffix + 1)]  # Finding n-gram features
    return _gramfeaturessuffix[0]


def addrowno(dataframe):
    docDF = dataframe
    docDF = docDF.sort_values(by=['y0'])  # type: object
    docDF['ydiff'] = docDF['y0'].diff()
    meanYDiff = docDF['ydiff'].mean()

    lineStartNo = 1
    currenLIneNo = lineStartNo
    for index, row in docDF.iterrows():
        if row['ydiff'] > 10:
            currenLIneNo = currenLIneNo + 1  # type: Union[int, Any]
            docDF.loc[index, 'linNo'] = currenLIneNo
        else:
            docDF.loc[index, 'linNo'] = currenLIneNo

    return docDF

#Sorting linewise and columnwise data
def ParaCode(df):

    docDF = df
    docDF = addrowno(dataframe=docDF)
    docDF.fillna(0, inplace=True)

    """
        To sort data with respect to line no and x0
    """
    docDF = docDF.sort_values(by=['linNo', 'x0'])
    docDF.fillna(0, inplace=True)
    # print(docDF)
    newdf = docDF.groupby('linNo')
    newdf.fillna(0, inplace=True)
    finaltextline = []
    for linNo, linNo_df in newdf:
        textline = []
        for index, space in linNo_df.iterrows():

            Text = linNo_df['Token'].get(index)
            textline.append(Text)
            textline = [' '.join(textline)]
        finaltextline.append(textline)

    df = pd.DataFrame(finaltextline)
    pd.set_option('display.max_colwidth', None)
    return df

######################################################################################################################################
''' Feature9: Specific for Date extraction'''
def extract_date(string):
    #print('string',string)
    string = string.replace(' -| /','-|/').replace('- |/ ', '-|/')
    date = re.findall(r'\d{1,2}/\d{1,2}/\d{1,4}|\d{1,4}/\d{1,2}/\d{1,2}|\d{1,2}-\d{1,2}-\d{1,4}|\d{1,4}-\d{1,2}-\d{1,2}|\d{1,2}\.\d{1,2}\.\d{1,4}', string)

    if not date:


        date = re.findall(r'''\d{1,4}\s{0,3}January\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Jan\s{0,3}\d{1,4}|\d{1,4}\s{0,3}JANUARY\s{0,3}\d{1,4}|\d{1,4}\s{0,3}JAN\s{0,3}\d{1,4}|\d{1,4}\s{0,3}jan\s{0,3}\d{1,4}|\d{1,4}\s{0,3}january\s{0,3}\d{1,4}|\d{1,4}\s{0,3}February\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Feb\s{0,3}\d{1,4}|\d{1,4}\s{0,3}FEBRUARY\s{0,3}\d{1,4}|\d{1,4}\s{0,3}FEB\s{0,3}\d{1,4}|\d{1,4}\s{0,3}february\s{0,3}\d{1,4}|\d{1,4}\s{0,3}feb\s{0,3}\d{1,4}|\d{1,4}\s{0,3}March\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Mar\s{0,3}\d{1,4}|\d{1,4}\s{0,3}MARCH\s{0,3}\d{1,4}|\d{1,4}\s{0,3}MAR\s{0,3}\d{1,4}|\d{1,4}\s{0,3}mar\s{0,3}\d{1,4}|\d{1,4}\s{0,3}march\s{0,3}\d{1,4}|\d{1,4}\s{0,3}April\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Apr\s{0,3}\d{1,4}|\d{1,4}\s{0,3}APRIL\s{0,3}\d{1,4}|\d{1,4}\s{0,3}APR\s{0,3}\d{1,4}|\d{1,4}\s{0,3}apr\s{0,3}\d{1,4}|\d{1,4}\s{0,3}april\s{0,3}\d{1,4}|\d{1,4}\s{0,3}May\s{0,3}\d{1,4}|\d{1,4}\s{0,3}May\s{0,3}\d{1,4}|\d{1,4}\s{0,3}MAY\s{0,3}\d{1,4}|\d{1,4}\s{0,3}may\s{0,3}\d{1,4}|\d{1,4}\s{0,3}June\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Jun\s{0,3}\d{1,4}|\d{1,4}\s{0,3}JUNE\s{0,3}\d{1,4}|\d{1,4}\s{0,3}JUN\s{0,3}\d{1,4}|\d{1,4}\s{0,3}june\s{0,3}\d{1,4}|\d{1,4}\s{0,3}jun\s{0,3}\d{1,4}|\d{1,4}\s{0,3}July\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Jul\s{0,3}\d{1,4}|\d{1,4}\s{0,3}JULY\s{0,3}\d{1,4}|\d{1,4}\s{0,3}JUL\s{0,3}\d{1,4}|\d{1,4}\s{0,3}August\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Aug\s{0,3}\d{1,4}|\d{1,4}\s{0,3}AUGUST\s{0,3}\d{1,4}|\d{1,4}\s{0,3}AUG\s{0,3}\d{1,4}|\d{1,4}\s{0,3}AUG\s{0,3}\d{1,4}|\d{1,4}\s{0,3}aug\s{0,3}\d{1,4}|\d{1,4}\s{0,3}august\s{0,3}\d{1,4}|\d{1,4}\s{0,3}September\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Sep\s{0,3}\d{1,4}|\d{1,4}\s{0,3}SEPTEMBER\s{0,3}\d{1,4}|\d{1,4}\s{0,3}SEP\s{0,3}\d{1,4}|\d{1,4}\s{0,3}september\s{0,3}\d{1,4}|\d{1,4}\s{0,3}sep\s{0,3}\d{1,4}|\d{1,4}\s{0,3}October\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Oct\s{0,3}\d{1,4}|\d{1,4}\s{0,3}OCTOBER\s{0,3}\d{1,4}|\d{1,4}\s{0,3}OCT\s{0,3}\d{1,4}|\d{1,4}\s{0,3}oct\s{0,3}\d{1,4}|\d{1,4}\s{0,3}october\s{0,3}\d{1,4}|\d{1,4}\s{0,3}November\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Nov\s{0,3}\d{1,4}|\d{1,4}\s{0,3}NOVEMBER\s{0,3}\d{1,4}|\d{1,4}\s{0,3}NOV\s{0,3}\d{1,4}|\d{1,4}\s{0,3}nov\s{0,3}\d{1,4}|\d{1,4}\s{0,3}november\s{0,3}\d{1,4}|\d{1,4}\s{0,3}December\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Dec\s{0,3}\d{1,4}|\d{1,4}\s{0,3}DECEMBER\s{0,3}\d{1,4}|\d{1,4}\s{0,3}DEC\s{0,3}\d{1,4}|\d{1,4}\s{0,3}DECEMBER\s{0,3}\d{1,4}|\d{1,4}\s{0,3}DEC\s{0,3}\d{1,4}|\d{1,4}\s{0,3}dec\s{0,3}\d{1,4}|\d{1,4}\s{0,3}december\d{1,4}\s{0,3}|
                      \d{1,4}\s{0,3}January\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Jan\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}JANUARY\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}JAN\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}jan\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}january\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}February\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Feb\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}FEBRUARY\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}FEB\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}february\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}feb\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}March\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Mar\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}MARCH\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}MAR\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}mar\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}march\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}April\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Apr\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}APRIL\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}APR\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}apr\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}april\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}May\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}May\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}MAY\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}may\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}June\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Jun\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}JUNE\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}JUN\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}june\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}jun\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}July\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Jul\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}JULY\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}JUL\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}August\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Aug\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}AUGUST\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}AUG\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}AUG\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}aug\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}august\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}September\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Sep\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}SEPTEMBER\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}SEP\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}september\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}sep\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}October\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Oct\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}OCTOBER\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}OCT\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}oct\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}october\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}November\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Nov\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}NOVEMBER\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}NOV\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}nov\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}november\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}December\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Dec\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}DECEMBER\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}DEC\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}DECEMBER\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}DEC\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}dec\'\s{0,3}\d{1,4}|\d{1,4}\s{0,3}december\'\s{0,3}\d{1,4}|
                      \d{1,4}January\'\s{0,3}\d{1,4}|\d{1,4}Jan\'\s{0,3}\d{1,4}|\d{1,4}JANUARY\'\s{0,3}\d{1,4}|\d{1,4}JAN\'\s{0,3}\d{1,4}|\d{1,4}jan\'\s{0,3}\d{1,4}|\d{1,4}january\'\s{0,3}\d{1,4}|\d{1,4}February\'\s{0,3}\d{1,4}|\d{1,4}Feb\'\s{0,3}\d{1,4}|\d{1,4}FEBRUARY\'\s{0,3}\d{1,4}|\d{1,4}FEB\'\s{0,3}\d{1,4}|\d{1,4}february\'\s{0,3}\d{1,4}|\d{1,4}feb\'\s{0,3}\d{1,4}|\d{1,4}March\'\s{0,3}\d{1,4}|\d{1,4}Mar\'\s{0,3}\d{1,4}|\d{1,4}MARCH\'\s{0,3}\d{1,4}|\d{1,4}MAR\'\s{0,3}\d{1,4}|\d{1,4}mar\'\s{0,3}\d{1,4}|\d{1,4}march\'\s{0,3}\d{1,4}|\d{1,4}April\'\s{0,3}\d{1,4}|\d{1,4}Apr\'\s{0,3}\d{1,4}|\d{1,4}APRIL\'\s{0,3}\d{1,4}|\d{1,4}APR\'\s{0,3}\d{1,4}|\d{1,4}apr\'\s{0,3}\d{1,4}|\d{1,4}april\'\s{0,3}\d{1,4}|\d{1,4}May\'\s{0,3}\d{1,4}|\d{1,4}May\'\s{0,3}\d{1,4}|\d{1,4}MAY\'\s{0,3}\d{1,4}|\d{1,4}may\'\s{0,3}\d{1,4}|\d{1,4}June\'\s{0,3}\d{1,4}|\d{1,4}Jun\'\s{0,3}\d{1,4}|\d{1,4}JUNE\'\s{0,3}\d{1,4}|\d{1,4}JUN\'\s{0,3}\d{1,4}|\d{1,4}june\'\s{0,3}\d{1,4}|\d{1,4}jun\'\s{0,3}\d{1,4}|\d{1,4}July\'\s{0,3}\d{1,4}|\d{1,4}Jul\'\s{0,3}\d{1,4}|\d{1,4}JULY\'\s{0,3}\d{1,4}|\d{1,4}JUL\'\s{0,3}\d{1,4}|\d{1,4}August\'\s{0,3}\d{1,4}|\d{1,4}Aug\'\s{0,3}\d{1,4}|\d{1,4}AUGUST\'\s{0,3}\d{1,4}|\d{1,4}AUG\'\s{0,3}\d{1,4}|\d{1,4}AUG\'\s{0,3}\d{1,4}|\d{1,4}aug\'\s{0,3}\d{1,4}|\d{1,4}august\'\s{0,3}\d{1,4}|\d{1,4}September\'\s{0,3}\d{1,4}|\d{1,4}Sep\'\s{0,3}\d{1,4}|\d{1,4}SEPTEMBER\'\s{0,3}\d{1,4}|\d{1,4}SEP\'\s{0,3}\d{1,4}|\d{1,4}september\'\s{0,3}\d{1,4}|\d{1,4}sep\'\s{0,3}\d{1,4}|\d{1,4}October\'\s{0,3}\d{1,4}|\d{1,4}Oct\'\s{0,3}\d{1,4}|\d{1,4}OCTOBER\'\s{0,3}\d{1,4}|\d{1,4}OCT\'\s{0,3}\d{1,4}|\d{1,4}oct\'\s{0,3}\d{1,4}|\d{1,4}october\'\s{0,3}\d{1,4}|\d{1,4}November\'\s{0,3}\d{1,4}|\d{1,4}Nov\'\s{0,3}\d{1,4}|\d{1,4}NOVEMBER\'\s{0,3}\d{1,4}|\d{1,4}NOV\'\s{0,3}\d{1,4}|\d{1,4}nov\'\s{0,3}\d{1,4}|\d{1,4}november\'\s{0,3}\d{1,4}|\d{1,4}December\'\s{0,3}\d{1,4}|\d{1,4}Dec\'\s{0,3}\d{1,4}|\d{1,4}DECEMBER\'\s{0,3}\d{1,4}|\d{1,4}DEC\'\s{0,3}\d{1,4}|\d{1,4}DECEMBER\'\s{0,3}\d{1,4}|\d{1,4}DEC\'\s{0,3}\d{1,4}|\d{1,4}dec\'\s{0,3}\d{1,4}|\d{1,4}december\'\s{0,3}\d{1,4}|
                      January\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|Jan\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|JANUARY\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|JAN\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|jan\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|january\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|February\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|Feb\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|FEBRUARY\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|FEB\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|february\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|feb\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|March\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|Mar\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|MARCH\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|MAR\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|mar\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|march\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|April\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|Apr\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|APRIL\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|APR\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|apr\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|april\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|May\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|May\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|MAY\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|may\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|June\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|Jun\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|JUNE\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|JUN\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|june\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|jun\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|July\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|Jul\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|JULY\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|JUL\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|August\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|Aug\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|AUGUST\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|AUG\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|AUG\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|aug\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|august\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|September\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|Sep\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|SEPTEMBER\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|SEP\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|september\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|sep\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|October\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|Oct\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|OCTOBER\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|OCT\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|oct\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|october\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|November\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|Nov\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|NOVEMBER\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|NOV\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|nov\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|november\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|December\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|Dec\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|DECEMBER\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|DEC\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|DECEMBER\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|DEC\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|dec\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|december\s{0,3}\d{1,2}\,\s{0,3}\d{1,4}|
                      \d{1,4}January\.\s{0,3}\d{1,4}|\d{1,4}Jan\.\s{0,3}\d{1,4}|\d{1,4}JANUARY\.\s{0,3}\d{1,4}|\d{1,4}JAN\.\s{0,3}\d{1,4}|\d{1,4}jan\.\s{0,3}\d{1,4}|\d{1,4}january\.\s{0,3}\d{1,4}|\d{1,4}February\.\s{0,3}\d{1,4}|\d{1,4}Feb\.\s{0,3}\d{1,4}|\d{1,4}FEBRUARY\.\s{0,3}\d{1,4}|\d{1,4}FEB\.\s{0,3}\d{1,4}|\d{1,4}february\.\s{0,3}\d{1,4}|\d{1,4}feb\.\s{0,3}\d{1,4}|\d{1,4}March\.\s{0,3}\d{1,4}|\d{1,4}Mar\.\s{0,3}\d{1,4}|\d{1,4}MARCH\.\s{0,3}\d{1,4}|\d{1,4}MAR\.\s{0,3}\d{1,4}|\d{1,4}mar\.\s{0,3}\d{1,4}|\d{1,4}march\.\s{0,3}\d{1,4}|\d{1,4}April\.\s{0,3}\d{1,4}|\d{1,4}Apr\.\s{0,3}\d{1,4}|\d{1,4}APRIL\.\s{0,3}\d{1,4}|\d{1,4}APR\.\s{0,3}\d{1,4}|\d{1,4}apr\.\s{0,3}\d{1,4}|\d{1,4}april\.\s{0,3}\d{1,4}|\d{1,4}May\.\s{0,3}\d{1,4}|\d{1,4}May\.\s{0,3}\d{1,4}|\d{1,4}MAY\.\s{0,3}\d{1,4}|\d{1,4}may\.\s{0,3}\d{1,4}|\d{1,4}June\.\s{0,3}\d{1,4}|\d{1,4}Jun\.\s{0,3}\d{1,4}|\d{1,4}JUNE\.\s{0,3}\d{1,4}|\d{1,4}JUN\.\s{0,3}\d{1,4}|\d{1,4}june\.\s{0,3}\d{1,4}|\d{1,4}jun\.\s{0,3}\d{1,4}|\d{1,4}July\.\s{0,3}\d{1,4}|\d{1,4}Jul\.\s{0,3}\d{1,4}|\d{1,4}JULY\.\s{0,3}\d{1,4}|\d{1,4}JUL\.\s{0,3}\d{1,4}|\d{1,4}August\.\s{0,3}\d{1,4}|\d{1,4}Aug\.\s{0,3}\d{1,4}|\d{1,4}AUGUST\.\s{0,3}\d{1,4}|\d{1,4}AUG\.\s{0,3}\d{1,4}|\d{1,4}AUG\.\s{0,3}\d{1,4}|\d{1,4}aug\.\s{0,3}\d{1,4}|\d{1,4}august\.\s{0,3}\d{1,4}|\d{1,4}September\.\s{0,3}\d{1,4}|\d{1,4}Sep\.\s{0,3}\d{1,4}|\d{1,4}SEPTEMBER\.\s{0,3}\d{1,4}|\d{1,4}SEP\.\s{0,3}\d{1,4}|\d{1,4}september\.\s{0,3}\d{1,4}|\d{1,4}sep\.\s{0,3}\d{1,4}|\d{1,4}October\.\s{0,3}\d{1,4}|\d{1,4}Oct\.\s{0,3}\d{1,4}|\d{1,4}OCTOBER\.\s{0,3}\d{1,4}|\d{1,4}OCT\.\s{0,3}\d{1,4}|\d{1,4}oct\.\s{0,3}\d{1,4}|\d{1,4}october\.\s{0,3}\d{1,4}|\d{1,4}November\.\s{0,3}\d{1,4}|\d{1,4}Nov\.\s{0,3}\d{1,4}|\d{1,4}NOVEMBER\.\s{0,3}\d{1,4}|\d{1,4}NOV\.\s{0,3}\d{1,4}|\d{1,4}nov\.\s{0,3}\d{1,4}|\d{1,4}november\.\s{0,3}\d{1,4}|\d{1,4}December\.\s{0,3}\d{1,4}|\d{1,4}Dec\.\s{0,3}\d{1,4}|\d{1,4}DECEMBER\.\s{0,3}\d{1,4}|\d{1,4}DEC\.\s{0,3}\d{1,4}|\d{1,4}DECEMBER\.\s{0,3}\d{1,4}|\d{1,4}DEC\.\s{0,3}\d{1,4}|\d{1,4}dec\.\s{0,3}\d{1,4}|\d{1,4}december\.\s{0,3}\d{1,4}|
                      \d{1,4}\s{0,3}January\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Jan\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}JANUARY\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}JAN\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}jan\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}january\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}February\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Feb\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}FEBRUARY\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}FEB\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}february\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}feb\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}March\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Mar\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}MARCH\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}MAR\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}mar\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}march\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}April\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Apr\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}APRIL\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}APR\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}apr\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}april\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}May\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}May\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}MAY\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}may\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}June\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Jun\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}JUNE\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}JUN\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}june\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}jun\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}July\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Jul\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}JULY\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}JUL\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}August\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Aug\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}AUGUST\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}AUG\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}AUG\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}aug\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}august\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}September\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Sep\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}SEPTEMBER\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}SEP\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}september\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}sep\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}October\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Oct\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}OCTOBER\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}OCT\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}oct\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}october\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}November\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Nov\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}NOVEMBER\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}NOV\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}nov\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}november\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}December\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Dec\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}DECEMBER\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}DEC\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}DECEMBER\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}DEC\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}dec\.\s{0,3}\d{1,4}|\d{1,4}\s{0,3}december\.\s{0,3}\d{1,4}|
                      \d{1,4}\s{0,3}January\.\d{1,4}|\d{1,4}\s{0,3}Jan\.\d{1,4}|\d{1,4}\s{0,3}JANUARY\.\d{1,4}|\d{1,4}\s{0,3}JAN\.\d{1,4}|\d{1,4}\s{0,3}jan\.\d{1,4}|\d{1,4}\s{0,3}january\.\d{1,4}|\d{1,4}\s{0,3}February\.\d{1,4}|\d{1,4}\s{0,3}Feb\.\d{1,4}|\d{1,4}\s{0,3}FEBRUARY\.\d{1,4}|\d{1,4}\s{0,3}FEB\.\d{1,4}|\d{1,4}\s{0,3}february\.\d{1,4}|\d{1,4}\s{0,3}feb\.\d{1,4}|\d{1,4}\s{0,3}March\.\d{1,4}|\d{1,4}\s{0,3}Mar\.\d{1,4}|\d{1,4}\s{0,3}MARCH\.\d{1,4}|\d{1,4}\s{0,3}MAR\.\d{1,4}|\d{1,4}\s{0,3}mar\.\d{1,4}|\d{1,4}\s{0,3}march\.\d{1,4}|\d{1,4}\s{0,3}April\.\d{1,4}|\d{1,4}\s{0,3}Apr\.\d{1,4}|\d{1,4}\s{0,3}APRIL\.\d{1,4}|\d{1,4}\s{0,3}APR\.\d{1,4}|\d{1,4}\s{0,3}apr\.\d{1,4}|\d{1,4}\s{0,3}april\.\d{1,4}|\d{1,4}\s{0,3}May\.\d{1,4}|\d{1,4}\s{0,3}May\.\d{1,4}|\d{1,4}\s{0,3}MAY\.\d{1,4}|\d{1,4}\s{0,3}may\.\d{1,4}|\d{1,4}\s{0,3}June\.\d{1,4}|\d{1,4}\s{0,3}Jun\.\d{1,4}|\d{1,4}\s{0,3}JUNE\.\d{1,4}|\d{1,4}\s{0,3}JUN\.\d{1,4}|\d{1,4}\s{0,3}june\.\d{1,4}|\d{1,4}\s{0,3}jun\.\d{1,4}|\d{1,4}\s{0,3}July\.\d{1,4}|\d{1,4}\s{0,3}Jul\.\d{1,4}|\d{1,4}\s{0,3}JULY\.\d{1,4}|\d{1,4}\s{0,3}JUL\.\d{1,4}|\d{1,4}\s{0,3}August\.\d{1,4}|\d{1,4}\s{0,3}Aug\.\d{1,4}|\d{1,4}\s{0,3}AUGUST\.\d{1,4}|\d{1,4}\s{0,3}AUG\.\d{1,4}|\d{1,4}\s{0,3}AUG\.\d{1,4}|\d{1,4}\s{0,3}aug\.\d{1,4}|\d{1,4}\s{0,3}august\.\d{1,4}|\d{1,4}\s{0,3}September\.\d{1,4}|\d{1,4}\s{0,3}Sep\.\d{1,4}|\d{1,4}\s{0,3}SEPTEMBER\.\d{1,4}|\d{1,4}\s{0,3}SEP\.\d{1,4}|\d{1,4}\s{0,3}september\.\d{1,4}|\d{1,4}\s{0,3}sep\.\d{1,4}|\d{1,4}\s{0,3}October\.\d{1,4}|\d{1,4}\s{0,3}Oct\.\d{1,4}|\d{1,4}\s{0,3}OCTOBER\.\d{1,4}|\d{1,4}\s{0,3}OCT\.\d{1,4}|\d{1,4}\s{0,3}oct\.\d{1,4}|\d{1,4}\s{0,3}october\.\d{1,4}|\d{1,4}\s{0,3}November\.\d{1,4}|\d{1,4}\s{0,3}Nov\.\d{1,4}|\d{1,4}\s{0,3}NOVEMBER\.\d{1,4}|\d{1,4}\s{0,3}NOV\.\d{1,4}|\d{1,4}\s{0,3}nov\.\d{1,4}|\d{1,4}\s{0,3}november\.\d{1,4}|\d{1,4}\s{0,3}December\.\d{1,4}|\d{1,4}\s{0,3}Dec\.\d{1,4}|\d{1,4}\s{0,3}DECEMBER\.\d{1,4}|\d{1,4}\s{0,3}DEC\.\d{1,4}|\d{1,4}\s{0,3}DECEMBER\.\d{1,4}|\d{1,4}\s{0,3}DEC\.\d{1,4}|\d{1,4}\s{0,3}dec\.\d{1,4}|\d{1,4}\s{0,3}december\.\d{1,4}|
                      \d{1,4}\s{0,3}January\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Jan\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}JANUARY\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}JAN\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}jan\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}january\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}February\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Feb\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}FEBRUARY\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}FEB\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}february\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}feb\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}March\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Mar\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}MARCH\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}MAR\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}mar\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}march\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}April\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Apr\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}APRIL\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}APR\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}apr\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}april\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}May\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}May\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}MAY\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}may\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}June\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Jun\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}JUNE\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}JUN\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}june\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}jun\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}July\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Jul\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}JULY\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}JUL\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}August\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Aug\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}AUGUST\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}AUG\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}AUG\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}aug\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}august\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}September\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Sep\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}SEPTEMBER\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}SEP\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}september\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}sep\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}October\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Oct\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}OCTOBER\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}OCT\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}oct\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}october\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}November\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Nov\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}NOVEMBER\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}NOV\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}nov\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}november\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}December\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}Dec\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}DECEMBER\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}DEC\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}DECEMBER\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}DEC\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}dec\,\s{0,3}\d{1,4}|\d{1,4}\s{0,3}december\,\s{0,3}\d{1,4}|
			\d{1,4}\/\s{0,3}January\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}Jan\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}JANUARY\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}JAN\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}jan\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}january\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}February\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}Feb\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}FEBRUARY\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}FEB\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}february\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}feb\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}March\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}Mar\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}MARCH\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}MAR\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}mar\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}march\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}April\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}Apr\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}APRIL\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}APR\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}apr\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}april\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}May\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}May\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}MAY\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}may\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}June\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}Jun\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}JUNE\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}JUN\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}june\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}jun\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}July\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}Jul\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}JULY\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}JUL\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}August\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}Aug\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}AUGUST\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}AUG\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}AUG\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}aug\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}august\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}September\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}Sep\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}SEPTEMBER\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}SEP\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}september\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}sep\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}October\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}Oct\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}OCTOBER\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}OCT\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}oct\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}october\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}November\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}Nov\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}NOVEMBER\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}NOV\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}nov\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}november\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}December\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}Dec\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}DECEMBER\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}DEC\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}DECEMBER\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}DEC\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}dec\/\s{0,3}\d{1,4}|\d{1,4}\/\s{0,3}december\/\s{0,3}\d{1,4}|
			\d{1,4}\-\s{0,3}January\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}Jan\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}JANUARY\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}JAN\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}jan\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}january\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}February\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}Feb\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}FEBRUARY\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}FEB\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}february\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}feb\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}March\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}Mar\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}MARCH\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}MAR\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}mar\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}march\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}April\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}Apr\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}APRIL\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}APR\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}apr\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}april\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}May\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}May\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}MAY\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}may\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}June\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}Jun\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}JUNE\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}JUN\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}june\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}jun\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}July\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}Jul\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}JULY\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}JUL\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}August\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}Aug\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}AUGUST\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}AUG\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}AUG\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}aug\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}august\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}September\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}Sep\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}SEPTEMBER\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}SEP\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}september\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}sep\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}October\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}Oct\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}OCTOBER\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}OCT\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}oct\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}october\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}November\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}Nov\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}NOVEMBER\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}NOV\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}nov\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}november\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}December\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}Dec\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}DECEMBER\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}DEC\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}DECEMBER\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}DEC\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}dec\-\s{0,3}\d{1,4}|\d{1,4}\-\s{0,3}december\-\s{0,3}\d{1,4}
                      ''', string)

    #print(date)
    if date:
        date = date[0]

    else:
        date = 'NA'
    return date

######################################################################################################################################

def cleantext(text):
    cleanedtext = []
    for text in text:

        textsplit = text.split()
        for text1 in textsplit:
            textstrip = text1.strip()
            cleanedtext.append(textstrip)
    return cleanedtext

#Cleaning the balance amount
def cleantotal(balance):
    data = re.sub(r'[^\d\.\s\,\-]','',balance)
    cleandata = data.replace(' .','.').replace('. ','.').replace(',','').replace('-','')
    return cleandata

