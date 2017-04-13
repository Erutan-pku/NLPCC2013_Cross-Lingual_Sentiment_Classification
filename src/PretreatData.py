#coding=utf-8
#-*- coding: UTF-8 -*- 
import sys
import time
sys.path.append('tools/')
from IO import *
from googleTr import google_translate_EtoC, google_translate_CtoE
import lxml.etree
import re


def translate(Datas, function) :
    pattern = re.compile(ur'(.+?[|。|！|？|\.|\?|\!])' ) 
    pattern2 = re.compile(ur'(.+?[|,|，|;|；])' ) 
    if function is google_translate_EtoC :
        sentence_length_max = 500
    elif function is google_translate_CtoE :
        sentence_length_max = 150
    else :
        assert False

    count = 0
    for data_i in Datas :
        count += 1
        print 'NO_%d : %s'%(count, data_i['id'])
        for field in ['summary', 'text'] :
            if len(data_i[field]) == 0 :
                continue
            result = []
            for line in data_i[field].split('\n') :
                if len(line) < sentence_length_max :
                    result.append(function(line))
                    continue
                result_i = []

                sentences = filter(None, re.split(pattern, line))
                for sentence in sentences:
                    if len(sentence) < sentence_length_max :
                        result_i.append(function(sentence))
                        continue
                    subsentences = filter(None, re.split(pattern2, sentence))
                    for subsentence in subsentences:
                        result_i.append(function(subsentence))
                result.append(' '.join(result_i))

            data_i[field] = '\n'.join(result)
            #time.sleep(0.5)
    return Datas

def loadDataFile(Path, Type) :
    doc = lxml.etree.parse(Path)
    Data = []
    count_noID = 0
    for node in doc.xpath('//item') :
        data_i = {}
        try :
            data_i['id']       = node.xpath('review_id/text()')[0]
        except :
            count_noID += 1
            data_i['id']       = Type + str(count_noID)

        data_i['summary']      = node.xpath('summary/text()')[0]
        try :
            data_i['polarity'] = node.xpath('polarity/text()')[0]
        except :
            data_i['polarity'] = 'None'
        try :
            data_i['text']     = node.xpath('text/text()')[0]
        except :
            data_i['text']     = ' '
        
        data_i['category'] = node.xpath('category/text()')[0]
        Data.append(data_i)
    return Data


def getData(Type) :
    path_sample  = '../data/'+Type+'/sample.data'
    path_train   = '../data/'+Type+'/train.data'
    path_unlabel = '../data/'+Type+'/unlabel.data'
    path_test    = '../data/'+Type+'/testResult.data'
    output_head = '../data/'+Type+'_'

    
    sample    = loadDataFile(path_sample, Type+'_sample')
    sample_en = translate(sample, google_translate_CtoE)
    #print len(sample)
    writeListofDict(output_head+'sample_cn' , sample)
    writeListofDict(output_head+'sample_en' , sample_en)

    train     = loadDataFile(path_train, Type+'_train')
    train_cn  = translate(train, google_translate_EtoC)
    #print len(train)
    writeListofDict(output_head+'train_cn'  , train_cn)
    writeListofDict(output_head+'train_en'  , train)

    unlabel   = loadDataFile(path_unlabel, Type+'_unlabel')
    unlabel_en= translate(unlabel, google_translate_CtoE)
    #print len(unlabel)
    writeListofDict(output_head+'unlabel_cn', unlabel)
    writeListofDict(output_head+'unlabel_en', unlabel_en)    

    test      = loadDataFile(path_test, Type+'_test')
    test_en   = translate(test, google_translate_CtoE)
    #print len(test)
    writeListofDict(output_head+'test_cn'   , test)                                                                                                             
    writeListofDict(output_head+'test_en'   , test_en)



if __name__ == '__main__':
    getData(sys.argv[1])
    #getData('book')
    #getData('music')
    #getData('dvd')
