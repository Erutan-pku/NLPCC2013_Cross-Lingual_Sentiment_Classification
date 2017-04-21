#coding=utf-8
#-*- coding: UTF-8 -*- 
import sys
import time
sys.path.append('tools/')
from IO import *  
import codecs
import json
import jieba
import math
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from sklearn import svm 



def FeatureExtraction(inputFile, outputFile, FeatureDict, tokenizer) :
    data = loadListofDict(inputFile, output_type='list')
    #print len(data)
    Data_output = []
    
    for passage in data :
        label = 0
        if 'polarity' in passage:
            label = 1 if passage['polarity'] == 'P' else -1
        feature_map = {}

        all_sentences = passage['summary'] + ' ' + passage['text']
        words = tokenizer(all_sentences)
        for word in words :
            if word in FeatureDict :
                key = FeatureDict[word]
                if not key in feature_map :
                    feature_map[key] = 0
                feature_map[key] += 1

        feature_list = [(key, feature_map[key]) for key in feature_map]
        feature_list = sorted(feature_list)
        
        Data_output.append({'feature_list':feature_list, 'label':label, 'id':passage['id']})

    json_dumps = lambda x : json.dumps(x, ensure_ascii=False)
    writeList(outputFile, Data_output, convert=json_dumps)

def getWordsCountFile(mode, tokenizer) :
    Positive_words = Counter()
    Negative_words = Counter()
    all_words = Counter()
    for type_1 in ['book', 'dvd', 'music'] :
        for type_2 in ['sample', 'train', 'unlabel', 'test'] :
            filename_t = '../data/%s_%s_%s'%(type_1, type_2, mode)
            print filename_t
            data = loadListofDict(filename_t, output_type='list')
            for passage in data : 
                all_sentences = passage['summary'] + ' ' + passage['text']
                words = tokenizer(all_sentences)
                for word in words :
                    if len(word.strip()) == 0 :
                        continue
                    all_words.count(word)
                    if 'polarity' in passage and passage['polarity']=='P':
                        Positive_words.count(word)
                    if 'polarity' in passage and passage['polarity']=='N':
                        Negative_words.count(word)
    convert = lambda x : '%s\t%d'%(x[0], x[1])
    writeList('../data/all_words_counts_'+mode, all_words.getSortedList(), convert=convert)
    writeList('../data/positive_words_counts_'+mode, Positive_words.getSortedList(), convert=convert)
    writeList('../data/negative_words_counts_'+mode, Negative_words.getSortedList(), convert=convert)
    print len(all_words)
    print len(Positive_words)
    print len(Negative_words)
def getFeatureDict(mode) :

    convert = lambda x : {line.split('\t')[0]:int(line.split('\t')[1])for line in x}
    all_words_counts = convert(loadLists('../data/all_words_counts_'+mode))
    positive_words_counts = convert(loadLists('../data/positive_words_counts_'+mode))
    negative_words_counts = convert(loadLists('../data/negative_words_counts_'+mode))
    
    pwc = positive_words_counts
    nwc = negative_words_counts
    getCount = lambda x,y : x[y]+1 if y in x else 1
    harmonic = lambda x,y : y / x + x / y


    word_all = set(positive_words_counts.keys()) | set(negative_words_counts.keys())
    feature_all = [word for word in word_all]
    #feature_all = [word for word in word_all if (math.log(getCount(pwc, word) + getCount(nwc, word)) + 1) * harmonic(getCount(pwc, word), getCount(nwc, word)) > 1]
    feature_all = list(set(feature_all))

    feature_dict = {feature_all[i]:i+1 for i in range(len(feature_all))}
    #for word in feature_all :
    #    print word
    return feature_dict


def parseDict(line) :
    ls = line.split(' ')
    ret = {}
    ret['type'] = ls[0].split('=')[1]
    ret['word'] = ls[2].split('=')[1]
    ret['post'] = ls[3].split('=')[1]
    ret['istm'] = ls[4].split('=')[1]
    ret['polarity'] = ls[5].split('=')[1]
    return ret
if __name__ == '__main__':
    wordnet_lemmatizer = WordNetLemmatizer()
    English_tokenizer = lambda x : [wordnet_lemmatizer.lemmatize(word).lower() for word in nltk.word_tokenize(x)]
    Chinese_tokenizer = lambda x : list(jieba.cut(x))
    """
    Enlgish_Dict = loadLists('../data/subjclueslen1-HLTEMNLP05.tff', convert=parseDict)
    print len(Enlgish_Dict)
    Enlgish_Dict = [(line['word'].lower()if not line['polarity']=='neutral'else'neutral') for line in Enlgish_Dict]
    Enlgish_Dict = list(set(Enlgish_Dict))
    Enlgish_Dict = {Enlgish_Dict[i]:i+1 for i in range(len(Enlgish_Dict))}
    print len(Enlgish_Dict)
    """

    #getWordsCountFile(mode='cn', tokenizer=Chinese_tokenizer)
    #getWordsCountFile(mode='en', tokenizer=English_tokenizer)
    Chinese_Dict = getFeatureDict(mode='cn')
    English_Dict = getFeatureDict(mode='en')
    print len(Chinese_Dict)
    print len(English_Dict)

    #"""
    for type1 in ['book', 'music', 'dvd']:
        for type2 in ['sample', 'train', 'test', 'unlabel'] :
            filename_en = '../data/%s_%s_en'%(type1, type2)
            print filename_en
            FeatureExtraction(filename_en, filename_en+'_feature', FeatureDict=English_Dict, tokenizer=English_tokenizer)
            
            filename_cn = '../data/%s_%s_cn'%(type1, type2)
            print filename_cn
            FeatureExtraction(filename_cn, filename_cn+'_feature', FeatureDict=Chinese_Dict, tokenizer=Chinese_tokenizer)
    #"""

