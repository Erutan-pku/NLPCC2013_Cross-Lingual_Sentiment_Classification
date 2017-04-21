#coding=utf-8
#-*- coding: UTF-8 -*- 
import sys
sys.path.append('../src/tools/')
from IO import *
import os


dir_ = 'self-training'
data_files = os.listdir('self-training')
split = lambda x : x.split('\t')
get_major = lambda x : x[15]
for data_file in data_files :
    #if not data_file.endswith('_200') :
    #    continue
    datas = loadLists('self-training/'+data_file, convert=split, ignoreFirstLine=True)
    for i in range(len(datas)) :
        datas[i].append(i)
    datas = sorted(datas, key = get_major, reverse=True)
    #if datas[0][-1] == 0 :
    #    continue
    print data_file
    print list2line([datas[0][13]+'%', datas[0][14]+'%', datas[0][15]+'%', datas[0][-1]], split='\t')
    print ''
    