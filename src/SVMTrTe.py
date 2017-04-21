#coding=utf-8
#-*- coding: UTF-8 -*- 
import sys
sys.path.append('tools/')
from IO import *
from sklearn import svm
from scipy.sparse import coo_matrix
import numpy as np
import json
import math
import codecs
import matplotlib.pyplot as plt



def getXY(fileNames, Datas=None) :
    #tf = lambda x : 1 if x > 0 else 0 # 75.65
    #tf = lambda x : x # 74.94
    #tf = lambda x, y : float(x) / y # 73.03 sum
    #tf = lambda x : 1+math.log(float(x)) # 75.82
    tf = lambda x, y : 0.5 + 0.5 * x / y # 77.18 max

    idf = lambda x, y : 1
    #idf = lambda x, y : math.log(float(y) / x) # 74.96
    #idf = lambda x, y : math.log(float(y) / (1 + x)) # 74.88
    #idf = lambda x, y : math.log(float(y) / x - 1) # 74.71
    
    X = []
    Y = []
    if Datas is None :
        Datas = []
        for fileName in fileNames :
            Datas += loadLists(fileName, convert=json.loads)
    idfCounter = Counter()
    for data in Datas :
        for feature in data['feature_list'] :
            idfCounter.count(feature[0])

    len_Data = len(Datas)
    max_x = 100000
    row, col, data_x = [], [], []
    for i, data in enumerate(Datas) :

        Y.append(data['label'])
        feature_n = [feature[1] for feature in data['feature_list']]
        if not len(feature_n) == 0 :
            feature_sum = sum(feature_n)
            feature_max = max(feature_n)
            
        for feature in data['feature_list'] :
            row.append(i)
            col.append(feature[0])
            data_x.append(tf(feature[1], feature_max) * idf(idfCounter.get(feature[0]), len_Data))
    X = coo_matrix((data_x, (row,col)), shape=(len_Data, max_x))
    #print len(Datas)
    return X, Y

def getXY_encn(type_str, mode='train') :
    if mode == 'train' :
        if not type_str == 'all' :
            en_Names = ['../data/%s_train_en_feature'%(type_str), '../data/%s_sample_en_feature'%(type_str)]
            cn_Names = ['../data/%s_train_cn_feature'%(type_str), '../data/%s_sample_cn_feature'%(type_str)]
        else :
            en_Names, cn_Names = [], []
            for type_s in ['book', 'music', 'dvd'] :
                en_Names += ['../data/%s_train_en_feature'%(type_s), '../data/%s_sample_en_feature'%(type_s)]
                cn_Names += ['../data/%s_train_cn_feature'%(type_s), '../data/%s_sample_cn_feature'%(type_s)]
    elif mode == 'test' :
        if not type_str == 'all' :
            en_Names = ['../data/%s_test_en_feature'%(type_str)]
            cn_Names = ['../data/%s_test_cn_feature'%(type_str)]
        else :
            en_Names, cn_Names = [], []
            for type_s in ['book', 'music', 'dvd'] :
                en_Names += ['../data/%s_test_en_feature'%(type_s)]
                cn_Names += ['../data/%s_test_cn_feature'%(type_s)]

    en_Datas = []
    for fileName in en_Names :
        en_Datas += loadLists(fileName, convert=json.loads)
    cn_Datas = []
    for fileName in cn_Names :
        cn_Datas += loadLists(fileName, convert=json.loads)

    len_Data = len(en_Datas)
    max_x = 200000
    row, col, data_x = [], [], []
    X, Y = [], []
    for i in range(len(en_Datas)) :
        Y.append(en_Datas[i]['label'])
        for feature in en_Datas[i]['feature_list'] :
            row.append(i)
            col.append(feature[0])
            data_x.append(feature[1])
        for feature in cn_Datas[i]['feature_list'] :
            row.append(i)
            col.append(feature[0]+100000)
            data_x.append(feature[1])
    X = coo_matrix((data_x, (row,col)), shape=(len_Data, max_x))
    #print len(en_Datas)
    return X, Y

def SimpleTest() :
    #"""
    results = [] 
    for type2 in ['en', 'cn'] :
        fileNames = []
        test_names = []
        for type1 in ['book', 'music', 'dvd']:
            fileNames += ['../data/%s_train_%s_feature'%(type1, type2), '../data/%s_sample_%s_feature'%(type1, type2)]
            test_names.append('../data/%s_test_%s_feature'%(type1, type2))
        x_train  , y_train  = getXY(fileNames)
        x_test   , y_test = getXY(test_names)
        clf = svm.LinearSVR(C = 0.05)
        clf.fit(x_train, y_train)
          
        result = clf.predict(x_test)
        #max_t, min_t = max(result), min(result)
        #result = [x / max_t if x > 0 else -x / min_t for x in result]
        results.append(result)

        count_true = sum([1 if result[i]*y_test[i]>0 else 0 for i in range(len(result))])
        print count_true * 100.0 / len(result)

    result_add = [results[0][i]+results[1][i]for i in range(len(results[0]))]
    count_true = sum([1 if result_add[i]*y_test[i]>0 else 0 for i in range(len(result_add))])
    print count_true * 100.0 / len(result_add)
    #"""
    result_add = [(abs(results[0][i]+results[1][i]), results[0][i]+results[1][i], y_test[i])for i in range(len(results[0]))]
    result_add = sorted(result_add, reverse=True)
    precision = []
    for i in range(100) :
        nn = int(len(result_add) / 1000.0 * (i + 1))
        count_true = sum([1 if result_add[i][1]*result_add[i][2]>0 else 0 for i in range(nn)])
        precision.append(count_true * 100.0 / nn)
    print precision
    plt.figure(1)
    x = np.linspace(0, 10, 100)
    plt.plot(x, precision)
    plt.grid(True)
    plt.show()
    #count_true = sum([1 if result_add[i]*y_test[i]>0 else 0 for i in range(len(result_add))])
    #print count_true * 100.0 / len(result_add)
    #"""
    """
    print 'all'
    x_train  , y_train  = getXY_encn(type_str='all', mode='train')
    x_test   , y_test   = getXY_encn(type_str='all', mode='test')
    clf = svm.LinearSVR()
    clf.fit(x_train, y_train)
      
    result = clf.predict(x_test)

    count_true = sum([1 if result[i]*y_test[i]>0 else 0 for i in range(len(result))])
    print count_true * 100.0 / len(result)

    #"""
    #for type1 in ['book', 'music', 'dvd']:
    """
        results = [] 
        for type2 in ['en', 'cn'] :
            print type1, type2
            fileNames = ['../data/%s_train_%s_feature'%(type1, type2), '../data/%s_sample_%s_feature'%(type1, type2)]
            x_train  , y_train  = getXY(fileNames)
            x_test   , y_test = getXY(['../data/%s_test_%s_feature'%(type1, type2)])

            clf = svm.LinearSVR()
            clf.fit(x_train, y_train)
              
            result = clf.predict(x_test)
            #max_t, min_t = max(result), min(result)
            #result = [x / max_t if x > 0 else -x / min_t for x in result]
            results.append(result)

            count_true = sum([1 if result[i]*y_test[i]>0 else 0 for i in range(len(result))])
            print count_true * 100.0 / 4000
        print type1

        result_add = [results[0][i]+results[1][i]for i in range(4000)]
        count_true = sum([1 if result_add[i]*y_test[i]>0 else 0 for i in range(len(result_add))])
        print count_true * 100.0 / len(result_add)

        #result_add = [results[0][i]+results[1][i]for i in range(4000) if results[0][i]*results[1][i]>1.]
        #y_test     = [y_test[i] for i in range(4000) if results[0][i]*results[1][i]>1.]
        #count_true = sum([1 if result_add[i]*y_test[i]>0 else 0 for i in range(len(result_add))])
        print len(result_add)
        print count_true * 100.0 / len(result_add)

    """
    """
        print type1
        x_train  , y_train  = getXY_encn(type_str=type1, mode='train')
        x_test   , y_test   = getXY_encn(type_str=type1, mode='test')
        clf = svm.LinearSVR()
        clf.fit(x_train, y_train)
          
        result = clf.predict(x_test)

        count_true = sum([1 if result[i]*y_test[i]>0 else 0 for i in range(len(result))])
        print count_true * 100.0 / 4000
    #"""

def coTraining() :
    output = codecs.open(sys.argv[1], "w", "utf-8")

    en_Names_train, cn_Names_train = [], []
    en_unlabeled  , cn_unlabeled   = [], []
    en_Names_test , cn_Names_test  = [], []

    for type_str in ['book', 'music', 'dvd']:
        en_Names_train += ['../data/%s_train_en_feature'%(type_str), '../data/%s_sample_en_feature'%(type_str)]
        cn_Names_train += ['../data/%s_train_cn_feature'%(type_str), '../data/%s_sample_cn_feature'%(type_str)]
        en_unlabeled   += loadLists('../data/%s_unlabel_en_feature'%(type_str), convert=json.loads)
        cn_unlabeled   += loadLists('../data/%s_unlabel_cn_feature'%(type_str), convert=json.loads)
        en_Names_test  += ['../data/%s_test_en_feature'%(type_str)]
        cn_Names_test  += ['../data/%s_test_cn_feature'%(type_str)]

    x_test_en , y_test_en = getXY(en_Names_test)
    x_test_cn , y_test_cn = getXY(cn_Names_test)
    
    en_Datas_train = []
    for fileName in en_Names_train :
        en_Datas_train += loadLists(fileName, convert=json.loads)
    cn_Datas_train = []
    for fileName in cn_Names_train :
        cn_Datas_train += loadLists(fileName, convert=json.loads)

    ignore_mark = True
    ignore_num  = int(sys.argv[2])#500

    while True :
        output_i = []
        #print len(en_Datas_train), len(cn_Datas_train)
        #print len(en_unlabeled),   len(cn_unlabeled)
        output_i += [len(en_Datas_train), len(cn_Datas_train), len(en_unlabeled), len(cn_unlabeled)]
        x_train_en , y_train_en = getXY(None, Datas=en_Datas_train)
        x_train_cn , y_train_cn = getXY(None, Datas=cn_Datas_train)

        clf_en, clf_cn = svm.LinearSVR(C = 0.05), svm.LinearSVR(C = 0.05)
        clf_en.fit(x_train_en, y_train_en)
        clf_cn.fit(x_train_cn, y_train_cn)
          
        result_test_en = clf_en.predict(x_test_en)
        result_test_cn = clf_cn.predict(x_test_cn)
        result_test_add = [result_test_en[i]+result_test_cn[i] for i in range(len(result_test_en))]
        assert len(result_test_en) == len(result_test_cn) and len(result_test_en) == 12000
        getRate = lambda x, y: len([1 for i in y if x[i]*y_test_cn[i] > 0])*100.0/len(y)
        rate_true_en = getRate(result_test_en, range(12000))
        rate_true_cn = getRate(result_test_cn, range(12000))
        rate_true_add = getRate(result_test_add, range(12000))
        #print 'test_result(en|cn|all):  %.2f  %.2f  %.2f'%(rate_true_en, rate_true_cn, rate_true_add)

        result_threeTypes = [result_test_en, result_test_cn, result_test_add]
        ranges = (range(4000), range(4000, 8000, 1), range(8000, 12000, 1), range(12000))
        for range_t in ranges :
            for result_t in result_threeTypes :
                #print '%.2f'%getRate(result_t, range_t)
                output_i.append('%.2f'%getRate(result_t, range_t))

        x_unlab_en , y_unlab_en = getXY(None, Datas=en_unlabeled)
        x_unlab_cn , y_unlab_cn = getXY(None, Datas=cn_unlabeled)


        result_unlab_en = clf_en.predict(x_unlab_en)
        #max_t, min_t = max(result_unlab_en), min(result_unlab_en)
        #result_unlab_en = [x / max_t if x > 0 else -x / min_t for x in result_unlab_en]

        result_unlab_cn = clf_cn.predict(x_unlab_cn)
        #max_t, min_t = max(result_unlab_cn), min(result_unlab_cn)
        #result_unlab_cn = [x / max_t if x > 0 else -x / min_t for x in result_unlab_cn]

        all_score = [result_unlab_en[i]+result_unlab_cn[i] for i in range(len(result_unlab_en))]
        #bound_n = int(0.005*len(result_unlab_en))
        bound_n = int(sys.argv[3])#100
        #en_score = [abs(result_unlab_en[i]) for i in range(len(result_unlab_en))]
        #bound_en = sorted(en_score, reverse=True)[bound_n]
        #cn_score = [abs(result_unlab_cn[i]) for i in range(len(result_unlab_cn))]
        #bound_cn = sorted(cn_score, reverse=True)[bound_n]
        #print bound_en, bound_cn
        if ignore_mark :
            ignore_mark = False
            bound_ignore = sorted(all_score, reverse=True)[ignore_num]
            ignore_id = [i for i in range(len(all_score)) if all_score[i]>bound_ignore]
            en_unlabeled = [en_unlabeled[i] for i in range(len(en_unlabeled)) if not i in ignore_id]
            cn_unlabeled = [cn_unlabeled[i] for i in range(len(cn_unlabeled)) if not i in ignore_id]
            #print bound_ignore
            output_i += [bound_ignore]
            output.write(list2line(output_i, split=u'\t')+'\n')
            output.flush()
            #print ''
            continue

        bound_all = sorted(all_score, reverse=True)[bound_n]
        #print bound_all
        output_i += [bound_all]


        used_id = [i for i in range(len(all_score)) if all_score[i]>bound_all]
        #print len(used_id)
        output_i += [len(used_id)]

        for i in used_id :
            en_unlabeled[i]['label'] = 1 if all_score[i] > 0 else -1
            cn_unlabeled[i]['label'] = 1 if all_score[i] > 0 else -1
            en_Datas_train.append(en_unlabeled[i])
            cn_Datas_train.append(cn_unlabeled[i])

        en_unlabeled = [en_unlabeled[i] for i in range(len(en_unlabeled)) if not i in used_id]
        cn_unlabeled = [cn_unlabeled[i] for i in range(len(cn_unlabeled)) if not i in used_id]

        #print ''
        output.write(list2line(output_i, split=u'\t')+'\n')
        output.flush()



coTraining()