import sys
import re
import xml.etree.ElementTree as ET
import Stemmer

inverted_index_path = sys.argv[1] + "/index.txt"
query = sys.argv[2]
query = query.lower()

fields = ['t','b','c','i','r','e']
stem_to_orig = {}
stemmer = Stemmer.Stemmer("english")

if(len(query)>1):
    if(query[1]==':'):
        query_split = query.split(' ')
        query_str = ""
        curr = ""
        for word in query_split:
            if(word.startswith("t:") or word.startswith("r:") or word.startswith("e:") or word.startswith("b:") or word.startswith("i:") or word.startswith("c:")):
                query_str += curr
                curr = ""
                curr += word[2:] + " "
            else:
                curr += word + " "
        if(curr!=""):
            query_str += curr
        query = query_str
def get_tokens(text):
    if(text is None or len(text)==0):
        return []
    tokens = re.split(r'[^A-Za-z0-9]+', text)
    return tokens

def stem(tokens):
    stemmed_tokens = []
    for token in tokens:
        stemmed_token = stemmer.stemWord(token)
        stem_to_orig[stemmed_token] = token
        stemmed_tokens.append(stemmed_token)
    return stemmed_tokens

tokens = get_tokens(query)
stemmed_tokens = stem(tokens)
stemmed_tokens = sorted(stemmed_tokens)
ptr=0
ifile = open(inverted_index_path,"r")
line = ifile.readline()
word,posting = line.split(':')
ans = {}
for i in range(0, len(stemmed_tokens)):
    if(stemmed_tokens[i]==''):
        continue
    ans[stem_to_orig[stemmed_tokens[i]]] = {}
    for j in range(0, len(fields)):
        ans[stem_to_orig[stemmed_tokens[i]]][fields[j]] = []
while(True):
    try:
        if(not line):
            break
        match=False
        while(word == stemmed_tokens[ptr]):
            match=True
            docs = posting.split('|')
            for doc in docs:
                if(len(doc)<=1):
                    continue
                try:
                    doc_no,fields = doc.split('-')
                except:
                    print("ERROR doc", doc)
                    print(len(doc))
                    exit(0)
                # print("doc no, field", doc_no, fields)
                doc_no = int(doc_no[1:])
                # print("doc_no", doc_no)
                fields = fields.split(',')
                # print("fields", fields)
                for field in fields:
                    if(len(field)==0):
                        continue
                    ans[stem_to_orig[word]][field[0]].append(doc_no)
            line = ifile.readline()
            word,posting = line.split(':')
        if(match):
            ptr = ptr + 1
            if(ptr == len(stemmed_tokens)):
                break
        else:
            if(stemmed_tokens[ptr]==''):
                ptr=ptr+1
                continue
            line = ifile.readline()
            word,posting = line.split(':')
    except:
        break #empty line at the end
print(ans)
ifile.close() 