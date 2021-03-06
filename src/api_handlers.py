# coding=utf-8
'''
Created on 14 Mar 2013

@author: Nicolas Van Labeke (https://github.com/vanch3d)

'''
from EssayAnalyser.se_main_v3 import top_level_procedure

## @todo: Added for backward compatibility with Python 2.6 (linux)
import sys
if sys.version_info < (2, 7):
    from EssayAnalyser.utils.counter import Counter
else:
    from collections import Counter
import numpy as np
from operator import itemgetter
from itertools import groupby

__mapkeyscore = {}

def getScore(keyword):
    if keyword in __mapkeyscore:
        return __mapkeyscore[keyword]
    else:
        return 0

# Get the lemma form of a keyword
def getLemma(keyword,myarray_ke):
    for (k,v) in myarray_ke.items():
        if keyword in v:
            return k
    return keyword + " ###"

# Build A JSON object out of the Ngram(s), with their score(s), count and form(s) 
def ngramToJSON(ngram_list,myarray_ke):
    jsonNGram = []
    for [win_words,count] in ngram_list:
        ngram=[getLemma(w,myarray_ke) for w in win_words]
        #key = ''.join(r1)
        score = [getScore(n) for n in ngram]
        jsonNGram.append({
            'ngram':win_words,
            'source':win_words,
            'count':count,
            'score':score})
    return jsonNGram

# Build A JSON object out of the lemma, with their score(s), count and form(s) 
def lemmaToJSON(keylemmas,myarray_ke):
    jsonNGram = []
    for w in keylemmas:
        #ngram=getLemma(w)
        v = myarray_ke[w]
        tally=Counter()
        for elem in v:
            tally[elem] += 1
            
        #score = getScore(w)
        jsonNGram.append({
            'ngram':[w],
            'source':[elem for (elem,count) in tally.items()],
            'count':len(v),
            'score':[getScore(w)]})
    return jsonNGram


def ngramToTree(ngram_list):
    treenode = []
    for [win_words,count] in ngram_list:
        subtree = []
        for kk in win_words:
            keywords = [ {'name': kk , 'mysize': getScore(kk), 'mycount': count, "colour":"#f9f0ab" } for x in range(count)]
            subtree.append({ 'name' : kk, 'children' : keywords})
            #gg = getLemma(kk)
            #v = myarray_ke[gg]
            #tally=Counter()
            #for elem in v:
            #    tally[elem] += 1
        
                #subtree = []    
            #for (elem,count) in tally.items():
            #    keywords = [ {'name': w , 'mysize': getScore(w), 'mycount': 1, "colour":"#f9f0ab" } for w in v if w==elem ]
            #    subtree.append({ 'name' : elem, 'children' : keywords})
                #tt = [{ 'name' : elem, 'children' : keywords}]
                #keywords = [ {'name': w , 'size': getScore(w), "colour":"#f9f0ab" } for w in v ]
                ##treenode.append({ 'name' : k, 'size': 1, "colour":"#f9f0ab" })
        treenode.append({ 'name' : ' '.join(win_words), 'children' : subtree})
   
    return treenode

def setDispersionNgram(ngramlist,myarray_ke,lemmas):
    for ngram in ngramlist:
        forms=[getLemma(_form,myarray_ke) for _form in ngram['ngram']]
        #kk=[idx for hh in forms for idx,w in enumerate(lemmas) if w==hh]
        #kk.sort()
        kk=[idx for idx,w in enumerate(lemmas) for hh in forms if w==hh]

        
        ranges = []
        #for k, g in groupby(enumerate(kk), lambda (i,x):i-x):
        for k, g in groupby(enumerate(kk), lambda i_x: i_x[0] - i_x[1]):
            group = map(itemgetter(1), g)
            if (len(group) == len(ngram['ngram'])):
                ranges = ranges + group
            
        ngram['dispersion'] = ranges
        h,b = np.histogram(ranges,bins=10, range=(0, len(lemmas)))
        ngram['trend'] = h.tolist()


def restructure_ngrams(struct):
    # reformat n-grams into unified structure
    keylemmas = struct['ke_data']['keylemmas']
    bigram_keyphrases = struct['ke_data']['bigram_keyphrases']
    trigram_keyphrases = struct['ke_data']['trigram_keyphrases']
    quadgram_keyphrases = struct['ke_data']['quadgram_keyphrases']
    myarray_ke = struct['ke_data']['myarray_ke']

    scoresNfreqs = struct['ke_data']['scoresNfreqs']

    # Build an associative array out of the keywords list
    for (word, score, r, c) in scoresNfreqs:
        __mapkeyscore[word] = score

    ngrams = {}
    ngrams['keywords'] = lemmaToJSON(keylemmas, myarray_ke)
    ngrams['bigrams'] = ngramToJSON(bigram_keyphrases, myarray_ke)
    ngrams['trigrams'] = ngramToJSON(trigram_keyphrases, myarray_ke)
    ngrams['quadgrams'] = ngramToJSON(quadgram_keyphrases, myarray_ke)
    struct['ngrams'] = ngrams

    # Get complete flat list of text's lemmas
    lemmas = [l for p in struct['se_data']['se_parasenttok'] for s in p for l in s['lemma']]

    # build dispersion arrays for lemma
    for ngram in ngrams['keywords']:
        hh = ngram['ngram'][0]
        kk = [idx for idx, w in enumerate(lemmas) if w == hh]
        ngram['dispersion'] = kk
        h, b = np.histogram(kk, bins=10, range=(0, len(lemmas)))
        ngram['trend'] = h.tolist()

    # build dispersion arrays for ngrams
    # TODO: dispersion does not work for key phrases; removed from data structure
    # setDispersionNgram(ngrams['bigrams'],myarray_ke,lemmas)
    # setDispersionNgram(ngrams['trigrams'],myarray_ke,lemmas)
    # setDispersionNgram(ngrams['quadgrams'],myarray_ke,lemmas)
    return struct


def Flask_process_text(text0,module="H810",task="TMA01"):
    essay = top_level_procedure(text0, None, None, None, "NVL",module,task)

    restructure_ngrams(essay)
    return essay


if __name__ == '__main__':
    import json,os
    import textwrap, string, pprint

    text = u'''1- Introduction
The resource had some accessibility features that were achieved by keeping the document Microsoft® Office Word based, thereby accessible for students using assistive technologies such as screen readers or voice controlled packages. I was then able to make the navigation of the text primarily through headings and styles. 
Headings can indicate sections and subsections in a long document and help any reader to understand different parts of the document and levels of importance. 
Students who use screen reading software such as JAWS can use the Document Map to navigate, which in turn helps the student to understand the content and to move around the document. If I had used direct formatting, which unfortunately I did on some occasions, then although I could make the text have the same visual effect it would not appear in the document map and any screen reading software would not have used it as a navigation tool. 
An added feature is that as a Word document a blind student could run the document through a Braille embossing printer to give a Braille written document.
    '''
    #essay = Flask_process_text(string.replace(textwrap.dedent(text),'\n',' '))
    essay = Flask_process_text(textwrap.dedent(text))

    print(json.dumps(essay, indent=4))
