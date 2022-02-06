import sys
import re
import time
import xml.etree.ElementTree as ET
import Stemmer
import math

qip = open("queries.txt","r")
sys.stdout = open("queries_op.txt","w")
fields = ['t','b','c','i','r','e'] 
weights = {'t':100, 'b':1, 'c':20, 'i':20, 'r':0.05, 'e':0.05}
N = 21384757
stemmer = Stemmer.Stemmer("english")
STOP_WORDS = set(['whence', 'here', 'show', 'were', 'why', "n't", 'the', 'whereupon', 'not', 'more', 'how', 'eight', 'indeed', 'i', 'only', 'via', 'nine', 're', 'themselves', 'almost', 'to', 'already', 'front', 'least', 'becomes', 'thereby', 'doing', 'her', 'together', 'be', 'often', 'then', 'quite', 'less', 'many', 'they', 'ourselves', 'take', 'its', 'yours', 'each', 'would', 'may', 'namely', 'do', 'whose', 'whether', 'side', 'both', 'what', 'between', 'toward', 'our', 'whereby', "'m", 'formerly', 'myself', 'had', 'really', 'call', 'keep', "'re", 'hereupon', 'can', 'their', 'eleven', '’m', 'even', 'around', 'twenty', 'mostly', 'did', 'at', 'an', 'seems', 'serious', 'against', "n't", 'except', 'has', 'five', 'he', 'last', '‘ve', 'because', 'we', 'himself', 'yet', 'something', 'somehow', '‘m', 'towards', 'his', 'six', 'anywhere', 'us', '‘d', 'thru', 'thus', 'which', 'everything', 'become', 'herein', 'one', 'in', 'although', 'sometime', 'give', 'cannot', 'besides', 'across', 'noone', 'ever', 'that', 'over', 'among', 'during', 'however', 'when', 'sometimes', 'still', 'seemed', 'get', "'ve", 'him', 'with', 'part', 'beyond', 'everyone', 'same', 'this', 'latterly', 'no', 'regarding', 'elsewhere', 'others', 'moreover', 'else', 'back', 'alone', 'somewhere', 'are', 'will', 'beforehand', 'ten', 'very', 'most', 'three', 'former', '’re', 'otherwise', 'several', 'also', 'whatever', 'am', 'becoming', 'beside', '’s', 'nothing', 'some', 'since', 'thence', 'anyway', 'out', 'up', 'well', 'it', 'various', 'four', 'top', '‘s', 'than', 'under', 'might', 'could', 'by', 'too', 'and', 'whom', '‘ll', 'say', 'therefore', "'s", 'other', 'throughout', 'became', 'your', 'put', 'per', "'ll", 'fifteen', 'must', 'before', 'whenever', 'anyone', 'without', 'does', 'was', 'where', 'thereafter', "'d", 'another', 'yourselves', 'n‘t', 'see', 'go', 'wherever', 'just', 'seeming', 'hence', 'full', 'whereafter', 'bottom', 'whole', 'own', 'empty', 'due', 'behind', 'while', 'onto', 'wherein', 'off', 'again', 'a', 'two', 'above', 'therein', 'sixty', 'those', 'whereas', 'using', 'latter', 'used', 'my', 'herself', 'hers', 'or', 'neither', 'forty', 'thereupon', 'now', 'after', 'yourself', 'whither', 'rather', 'once', 'from', 'until', 'anything', 'few', 'into', 'such', 'being', 'make', 'mine', 'please', 'along', 'hundred', 'should', 'below', 'third', 'unless', 'upon', 'perhaps', 'ours', 'but', 'never', 'whoever', 'fifty', 'any', 'all', 'nobody', 'there', 'have', 'anyhow', 'of', 'seem', 'down', 'is', 'every', '’ll', 'much', 'none', 'further', 'me', 'who', 'nevertheless', 'about', 'everywhere', 'name', 'enough', '’d', 'next', 'meanwhile', 'though', 'through', 'on', 'first', 'been', 'hereby', 'if', 'move', 'so', 'either', 'amongst', 'for', 'twelve', 'nor', 'she', 'always', 'these', 'as', '’ve', 'amount', '‘re', 'someone', 'afterwards', 'you', 'nowhere', 'itself', 'done', 'hereafter', 'within', 'made', 'ca', 'them'])
def get_tokens(text):
    if(text is None or len(text)==0):
        return []
    tokens = re.split(r'[^A-Za-z0-9]+', text)
    return tokens

def stem(tokens):
    stemmed_tokens = []
    for token in tokens:
        stemmed_token = stemmer.stemWord(token)
        # stem_to_orig[stemmed_token] = token
        stemmed_tokens.append(stemmed_token)
    return stemmed_tokens


def parse_field_query(query):
    query_split = query.split(' ')
    query_str = []
    curr = ""
    for word in query_split:
        if(word.startswith("t:") or word.startswith("r:") or word.startswith("e:") or word.startswith("b:") or word.startswith("i:") or word.startswith("c:")):
            if(len(curr) > 0):
                query_str.append([curr[0], curr[2:]])
            curr = ""
            curr += word + " "
        else:
            curr += word + " "
    if(curr!=""):
        query_str.append([curr[0], curr[2:]])
    return query_str


def load_titles():
    titles_arr = []
    for i in range(0, 26):
        f = open("titles/" + str(i))
        titles_arr.append([])
        while(True):
            title = f.readline()
            if(not title):
                break
            titles_arr[i].append(title)
        f.close()
    return titles_arr

def get_title(doc_id):
    f = None
    first = False
    if(doc_id < 50000):
        f = open("titles/0", "r")
        first = True
    else:
        f_id = int(doc_id/50000)
        f = open("titles/" + str(f_id), "r")
    f_idx = doc_id % 50000
    i=0
    title = f.readline()
    while(title):
        if(first):
            if(i == doc_id-1):
                return title
        else:
            if(i==f_idx):
                return title
        i+=1
        title = f.readline()
    return "no-title" #not possible.





def search(req_field, term):
    f=None
    if(len(term) < 2):
        if(ord(term[0]) < 97):
            f = open("sec_inverted_index/" + "#" + "/" + term[0], "r")    
        else:
            f = open("sec_inverted_index/" + term[0] + "/" + term[0] + "0", "r")
    else:
        if(ord(term[0]) < 97):
            f = open("sec_inverted_index/" + "#" + "/" + term[0], "r")
        else:
            if(ord(term[1]) < 97):
                f = open("sec_inverted_index/" + term[0] + "/" + term[0] + "#", "r")
            else:
                f = open("sec_inverted_index/" + term[0] + "/" + term[0] + term[1], "r")

    line = f.readline()
    found = False
    while(line):
        word,posting = line.split(':')
        if(word == term):
            found = True
            docs = posting.split('|')
            idf = math.log(N/len(docs))
            for doc in docs:
                tf = 0
                try:
                    doc_no,vector = doc.split('-')
                    doc_no = int(doc_no[1:])
        
                    vector = vector.split(',')

                    for field in vector:
                        if(field[0] == req_field):
                            tf = weights[field[0]]*int(field[1:])
                            break
                    
                    if(doc_no in score):
                        score[doc_no] += idf*math.log(1 + tf)
                    else:
                        score[doc_no] = idf*math.log(1 + tf)
                except:
                    continue
        else:
            if(found):
                break
        line = f.readline()


def search_normal(term):
    f=None
    if(len(term) < 2):
        if(ord(term[0]) < 97):
            f = open("sec_inverted_index/" + "#" + "/" + term[0], "r")    
        else:
            f = open("sec_inverted_index/" + term[0] + "/" + term[0] + "0", "r")
    else:
        if(ord(term[0]) < 97):
            f = open("sec_inverted_index/" + "#" + "/" + term[0], "r")
        else:
            if(ord(term[1]) < 97):
                f = open("sec_inverted_index/" + term[0] + "/" + term[0] + "#", "r")
            else:
                f = open("sec_inverted_index/" + term[0] + "/" + term[0] + term[1], "r")

    line = f.readline()
    found = False
    while(line):
        word,posting = line.split(':')
        if(word == term):
            found = True
            docs = posting.split('|')
            idf = math.log(N/len(docs))
            for doc in docs:
                tf = 0
                try:
                    doc_no,vector = doc.split('-')
                    doc_no = int(doc_no[1:])
                    vector = vector.split(',')
                    for field in vector:
                        if(len(field) < 1):
                            continue
                        tf += weights[field[0]]*int(field[1:])  
                    if(doc_no in score):
                        score[doc_no] += idf*math.log(1 + tf)
                    else:
                        score[doc_no] = idf*math.log(1 + tf)
                except:
                    continue
        else:
            if(found):
                break
        line = f.readline()


for queries in qip.readlines():
    score = {}
    query = queries.strip().lower()
    st = time.time()
    if(len(query)>1):
        if(query[1]==':'):
            query_str = parse_field_query(query)
            # print(query_str)
            for query_term in query_str:
                # print(query_term)
                for term in query_term[1].split(' '):
                    if(len(term) < 1):
                        continue
                    if(term in STOP_WORDS):
                        continue
                    search(query_term[0], stemmer.stemWord(term))
        else:
            query_str = query.split(' ')
            for term in query_str:
                if(len(term) < 1):
                    continue
                if(term in STOP_WORDS):
                    continue
                search_normal(stemmer.stemWord(term))
        score = dict(sorted(score.items(), key=lambda item: item[1], reverse=True))
        nr = 10
        i=0
        et = time.time()
        for k,v in score.items():
            if(i == nr):
                break
            title_result = get_title(k)
            if(title_result=="out of title files"):
                print("error: doc id:", k)
                continue
            print(str(k)+", "+get_title(k),end='')
            i += 1
        print(et-st)
        print()
