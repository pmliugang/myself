# -*- coding: utf-8 -*-

import re
from numpy import *

def createData(fileName):
    mat = []
    req = re.compile(r',') # 正则表达式模式串
    fr = open(fileName)
    content = fr.readlines()
    for line in content:
        tem = line.replace('\n','').split(',')
        mat.append(tem)
    fr.close()
    return mat

def createC1(dataSet):
    '''
    创建一个包含所有项的不变集合
    param dataSet | list
    return 
    '''
    C1 = []
    for transaction in dataSet:
        for item in transaction:
            if not [item] in C1:
                C1.append([item])
    C1.sort()
    return map(frozenset, C1)  # 

def scanD(D, Ck, minSupport):
    '''
    # 计算所有项集的支持度
    param D | map-object
    param Ck
    param minSupport
    '''
    ssCnt = {}
    for tid in D:
        for can in Ck:
            if can.issubset(tid):
                if not can is ssCnt:
                    ssCnt[can] = 1
                else:
                    ssCnt[can] += 1
    numItems = float(len(list(D)))
    retList = []
    supportData = {}
    for key in ssCnt:
        try:
            support = ssCnt[key] / numItems
        except:
            continue
        else:
            if support >= minSupport:
                retList.insert(0, key)
            supportData[key] = support
    return retList, supportData

def aprioriGen(Lk, k):
    '''
    创建候选集
    param Lk
    param k
    return
    '''
    retList = []  # 创建空列表
    lenLk = len(Lk)  # 计算LK中像素的个数
    for i in range(lenLk):
        for j in range(i + 1, lenLk):
            L1 = list(Lk[i])[:k - 2];
            L2 = list(Lk[j])[:k - 2]
            L1.sort();
            L2.sort()
            if L1 == L2:  # 如果前面K-2个元素都相等
                retList.append(Lk[i] | Lk[j])  # 合并
    return retList

def apriori(dataSet, minSupport=0.5):
    '''
    调用关联程序
    '''
    C1 = createC1(dataSet)
    D = map(set, dataSet) # 
    L1, supportData = scanD(D, C1, minSupport)
    L = [L1]
    k = 2
    while (len(L[k - 2]) > 0):
        Ck = aprioriGen(L[k - 2], k)
        Lk, supK = scanD(D, Ck, minSupport)
        supportData.update(supK)
        L.append(Lk)
        k += 1
    return L, supportData

def generateRules(fileName, L, supportData, minConf=0.7):  # supportData是从scanD获得的字段
    '''
    关联规则
    '''
    bigRuleList = []
    for i in range(1, len(L)):  # 只获得又有2个或以上的项目的集合
        for freqSet in L[i]:
            H1 = [frozenset([item]) for item in freqSet]
            if (i > 1):
                rulesFromConseq(fileName, freqSet, H1, supportData, bigRuleList, minConf)
            else:
                calcConf(fileName, freqSet, H1, supportData, bigRuleList, minConf)
    return bigRuleList


def calcConf(fileName, freqSet, H, supportData, brl, minConf=0.7):
    '''
    实例数、支持度、置信度和提升度评估
    '''
    prunedH = []
    D = createData(fileName)
    numItems = float(len(D))
    for conseq in H:
        conf = supportData[freqSet] / supportData[freqSet - conseq]  # 计算置信度
        if conf >= minConf:
            instances = numItems * supportData[freqSet]  # 计算实例数
            liftvalue = conf / supportData[conseq]  # 计算提升度
            brl.append((freqSet - conseq, conseq, int(instances), round(supportData[freqSet], 4), round(conf, 4),
                        round(liftvalue, 4)))  # 支持度已经在SCAND中计算得出
            prunedH.append(conseq)
    return prunedH


def rulesFromConseq(fileName, freqSet, H, supportData, brl, minConf=0.7):
    '''
    生成候选规则集
    '''
    m = len(H[0])
    if (len(freqSet) > (m + 1)):
        Hmp1 = aprioriGen(H, m + 1)
        Hmp1 = calcConf(fileName, freqSet, Hmp1, supportData, brl, minConf)
        if (len(Hmp1) > 1):
            rulesFromConseq(fileName, freqSet, Hmp1, supportData, brl, minConf)
