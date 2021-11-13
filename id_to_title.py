import os
import sys
import re
import xml.etree.ElementTree as ET
import Stemmer
import time
import heapq
'''
{token : {page_no:[0,0,0,0,0,0]}} #title,body/text,category,infobox,ref,ext_links
'''

# wiki_dump_path = sys.argv[1]
wiki_dump_path = "enwiki-20210720-pages-articles-multistream.xml"

# if(not os.path.exists(os.path.dirname(wiki_dump_path))):
#     os.makedirs(os.path.dirname(wiki_dump_path))

# inverted_index_path = sys.argv[2] + "/index.txt"

# if(not os.path.exists(os.path.dirname(inverted_index_path))):
#     os.makedirs(os.path.dirname(inverted_index_path))

if(not os.path.exists("sub_indexes")):
    os.makedirs("sub_indexes")
if(not os.path.exists("inverted_index")):
    os.makedirs("inverted_index")

# stat_path = sys.argv[3]

postings = [{},{},{},{},{},{},{},{}]
text = ""
title = None
id = None
in_revision = False
in_page = False
page_id=1
file_id=0
pages_per_file=720000
# terms_per_file=4000000
terms_per_file=1000000
total_tokens=0
index_tokens=0
index_tokens2=0
field_to_index = {'t':0, 'b':1, 'c':2, 'i':3, 'r':4, 'e':5}
index_to_field = {0:'t', 1:'b', 2:'c', 3:'i', 4:'r', 5:'e'}
char_to_postings_index = {'a':0, 'b':0, 'c':0,'d':1,'e':1,'f':1, 'g':2, 'h':2, 'i':2, 'j':3, 'k':3, 'l':3, 'm':4, 'n':4, 'o':4, 'p':5, 'q':5, 'r':5, 's':6, 't':6, 'u':6, 'v':6, 'w':7, 'x':7, 'y':7, 'z':7}
postings_index_to_char = {0:'a-c', 1:'d-f', 2:'g-i', 3:'j-l', 4:'m-o', 5:'p-r', 6:'s-v', 7:'w-z'}
sub_indexes_id = [0,0,0,0,0,0,0,0] #number of files created for each subindex
sub_indexes_terms = [0,0,0,0,0,0,0,0] #count of terms in each subindex

stemmer = Stemmer.Stemmer("english")
STOP_WORDS = set(['whence', 'here', 'show', 'were', 'why', 'n’t', 'the', 'whereupon', 'not', 'more', 'how', 'eight', 'indeed', 'i', 'only', 'via', 'nine', 're', 'themselves', 'almost', 'to', 'already', 'front', 'least', 'becomes', 'thereby', 'doing', 'her', 'together', 'be', 'often', 'then', 'quite', 'less', 'many', 'they', 'ourselves', 'take', 'its', 'yours', 'each', 'would', 'may', 'namely', 'do', 'whose', 'whether', 'side', 'both', 'what', 'between', 'toward', 'our', 'whereby', "'m", 'formerly', 'myself', 'had', 'really', 'call', 'keep', "'re", 'hereupon', 'can', 'their', 'eleven', '’m', 'even', 'around', 'twenty', 'mostly', 'did', 'at', 'an', 'seems', 'serious', 'against', "n't", 'except', 'has', 'five', 'he', 'last', '‘ve', 'because', 'we', 'himself', 'yet', 'something', 'somehow', '‘m', 'towards', 'his', 'six', 'anywhere', 'us', '‘d', 'thru', 'thus', 'which', 'everything', 'become', 'herein', 'one', 'in', 'although', 'sometime', 'give', 'cannot', 'besides', 'across', 'noone', 'ever', 'that', 'over', 'among', 'during', 'however', 'when', 'sometimes', 'still', 'seemed', 'get', "'ve", 'him', 'with', 'part', 'beyond', 'everyone', 'same', 'this', 'latterly', 'no', 'regarding', 'elsewhere', 'others', 'moreover', 'else', 'back', 'alone', 'somewhere', 'are', 'will', 'beforehand', 'ten', 'very', 'most', 'three', 'former', '’re', 'otherwise', 'several', 'also', 'whatever', 'am', 'becoming', 'beside', '’s', 'nothing', 'some', 'since', 'thence', 'anyway', 'out', 'up', 'well', 'it', 'various', 'four', 'top', '‘s', 'than', 'under', 'might', 'could', 'by', 'too', 'and', 'whom', '‘ll', 'say', 'therefore', "'s", 'other', 'throughout', 'became', 'your', 'put', 'per', "'ll", 'fifteen', 'must', 'before', 'whenever', 'anyone', 'without', 'does', 'was', 'where', 'thereafter', "'d", 'another', 'yourselves', 'n‘t', 'see', 'go', 'wherever', 'just', 'seeming', 'hence', 'full', 'whereafter', 'bottom', 'whole', 'own', 'empty', 'due', 'behind', 'while', 'onto', 'wherein', 'off', 'again', 'a', 'two', 'above', 'therein', 'sixty', 'those', 'whereas', 'using', 'latter', 'used', 'my', 'herself', 'hers', 'or', 'neither', 'forty', 'thereupon', 'now', 'after', 'yourself', 'whither', 'rather', 'once', 'from', 'until', 'anything', 'few', 'into', 'such', 'being', 'make', 'mine', 'please', 'along', 'hundred', 'should', 'below', 'third', 'unless', 'upon', 'perhaps', 'ours', 'but', 'never', 'whoever', 'fifty', 'any', 'all', 'nobody', 'there', 'have', 'anyhow', 'of', 'seem', 'down', 'is', 'every', '’ll', 'much', 'none', 'further', 'me', 'who', 'nevertheless', 'about', 'everywhere', 'name', 'enough', '’d', 'next', 'meanwhile', 'though', 'through', 'on', 'first', 'been', 'hereby', 'if', 'move', 'so', 'either', 'amongst', 'for', 'twelve', 'nor', 'she', 'always', 'these', 'as', '’ve', 'amount', '‘re', 'someone', 'afterwards', 'you', 'nowhere', 'itself', 'done', 'hereafter', 'within', 'made', 'ca', 'them'])

def get_tokens(text):
    if(text is None or len(text)==0):
        return []
    tokens = re.split(r'[^A-Za-z0-9]+', text)
    return tokens


def parse_field(field, content):
    field_index = field_to_index[field]
    field_tokens = get_tokens(content)
    for field_token in field_tokens:
        posting_index = char_to_postings_index[field_token[0]]
        #posting = postings[posting_index]
        if(field_token in postings[posting_index]):
            if(page_id not in postings[posting_index][field_token]):
                postings[posting_index][field_token][page_id] = [0,0,0,0,0,0]
        else:
            postings[posting_index][field_token] = {}
            postings[posting_index][field_token][page_id] = [0,0,0,0,0,0]
        postings[posting_index][field_token][page_id][field_index] += 1

def index_field(field, content):
    global index_tokens2
    field_index = field_to_index[field]
    field_tokens = get_tokens(content)
    for field_token in field_tokens:
        if(field_token in STOP_WORDS):
            continue
        field_token = stemmer.stemWord(field_token)
        if(not field_token or len(field_token)==0):
            continue
        if(field_token[0] not in char_to_postings_index):
            # posting_index = 0
            continue
        else:
            posting_index = char_to_postings_index[field_token[0]]
        if(field_token in postings[posting_index]):
            if(page_id not in postings[posting_index][field_token]):
                postings[posting_index][field_token][page_id] = [0,0,0,0,0,0]
        else:
            postings[posting_index][field_token] = {}
            postings[posting_index][field_token][page_id] = [0,0,0,0,0,0]
        postings[posting_index][field_token][page_id][field_index] += 1
        sub_indexes_terms[posting_index] += 1
        index_tokens2 += 1
        # if(len(postings[posting_index]) == terms_per_file):
        if(sub_indexes_terms[posting_index] == terms_per_file):
            save(posting_index)



def extract_references(text):
    references_list = text.split("==references==") 
    if(len(references_list) <= 1):
        references_list = text.split("== references ==")
        if(len(references_list) <= 1):
            references_list = text.split("== references==")
            if(len(references_list) <= 1):
                references_list = text.split("==references ==")
    if(len(references_list) <= 1):
        return
        # return
    references_list = references_list[1].split('\n')
    references = ""
    for reference in references_list:
        if(len(reference)==0):
            continue
        if(reference[0]=='{'):
            if('reflist' in reference):
                continue
            if('http' not in reference and 'https' not in reference and 'cite' not in reference):
                break
        if(reference[0]=='=='):
            break
        references += reference + " "
    index_field('r',references)

def extract_category(text):
    category_list = re.findall(r"\[\[category:(.*)\]\]", text)
    text = re.sub(r"\[\[category:(.*)\]\]", "", str(text), flags=re.DOTALL)
    categories = ""
    for category in category_list:
        categories += category + " "
    index_field('c',categories)

def extract_external_links(text): 
    external_links_list = text.split("== external links ==")
    if(len(external_links_list)<=1):
        external_links_list = text.split("==external links==")
        if(len(external_links_list)<=1):
            external_links_list = text.split("== external links==")
            if(len(external_links_list)<=1):
                external_links_list = text.split("==external links ==")
    if(len(external_links_list)<=1):
        return
    external_links_list = re.findall(r"\[(http.*|https.*)\]", external_links_list[1],re.MULTILINE)
    external_links = ""
    for external_link in external_links_list:
        external_links += external_link + " "
    index_field('e',external_links)

def extract_infobox(text):
    infobox_list=re.findall(r'{{infobox((.|\n)*?)}}', text)
    text = re.sub(r'{{infobox((.|\n)*?)}}', "", str(text), flags=re.DOTALL)
    infoboxes = ""
    for infobox in infobox_list:
        for sub_infobox in infobox:
            infoboxes += sub_infobox + " "
    index_field('i',infoboxes)

def save(posting_index):
    global sub_indexes_id
    global sub_indexes_terms
    global postings
    # f = open(str(file_id), "w")
    f = open("sub_indexes/" + postings_index_to_char[posting_index] + str(sub_indexes_id[posting_index]), "w")
    for word in sorted(postings[posting_index].keys()):
        line=word+":"
        for page in postings[posting_index][word]:
            line += "d"+str(page)+"-"
            field_counts = postings[posting_index][word][page]
            for i,count in enumerate(field_counts):
                if(count):
                    line += index_to_field[i]+str(count)+","
            line += "|"
        line += "\n"
        f.write(line)
    f.close()
    postings[posting_index] = {}
    sub_indexes_terms[posting_index] = 0
    sub_indexes_id[posting_index] += 1


class DataWrap:
    def __init__(self, data):
        self.data = data  
    def __lt__(self, other):
        return self.data[0].split(':')[0] < other.data[0].split(':')[0]

def merge(posting_index):
    global index_tokens
    prev = ""
    file_handles = []
    heap = []
    # sorted_file = open(inverted_index_path,"w")
    sorted_file = open("inverted_index/" + postings_index_to_char[posting_index],"w")

    # for i in range(0,file_id+1):
    for i in range(0,sub_indexes_id[posting_index]+1):
        # file_handles.append(open(str(i),"r"))
        file_handles.append(open("sub_indexes/" + postings_index_to_char[posting_index] + str(i),"r"))
        first = file_handles[i].readline()
        if(not(len(first)==0 or (':' not in first) or (len(first.split(':')[0])==0))):
            heapObj = DataWrap([first, i])
            heapq.heappush(heap, heapObj)    
        heapObj = DataWrap([file_handles[i].readline(), i])
        heapq.heappush(heap, heapObj)

    while(len(heap)>0):
        element = heapq.heappop(heap)
        sorted_file.write(element.data[0])
        curr = element.data[0].split(':')[0]
        if(curr!=prev):
            index_tokens += 1
        prev=curr
        insert_line = file_handles[element.data[1]].readline()
        if(not insert_line):
            continue
        heapq.heappush(heap, DataWrap([insert_line, element.data[1]]))





def main():
    global page_id
    global file_id
    global in_page
    global title
    global pages_per_file
    global postings
    global char_to_postings_index
    global sub_indexes_id
    global in_revision
    global id
    global text
    global total_tokens
    start_time = time.time()
    for event, element in ET.iterparse(wiki_dump_path, events=('start','end')):
        tag = element.tag
        tag_stripped = re.sub(r'\{[^()]*\}','',tag)
        if(event=='start'):
            if(element.text is not None):
                total_tokens += len(element.text.split())
            if(tag_stripped=='page'):
                in_page = True
            elif(tag_stripped=='revision'):
                in_revision = True
            elif(in_page==True and title is None and tag_stripped=='title'):
                title = element.text
            elif(in_page==True and id is None and tag_stripped=='id'):
                id = element.text
            elif(in_page==True and tag_stripped=='text' and element.text is not None):
                text += element.text
        elif(event=='end'):
            if(tag_stripped=='page'):
                # if(page_id % pages_per_file==0):
                #     save()
                #     file_id += 1
                #     postings = {}
                # field_to_index = {'t':0, 'b':1, 'c':2, 'i':3, 'r':4, 'e':5}
                text = text.casefold()
                if(title is not None):
                    title = title.casefold()
                index_field('t',title)
                index_field('b',text)
                extract_category(text)
                extract_infobox(text)
                extract_references(text)
                extract_external_links(text)

                page_id += 1
                in_page=False
                in_revision = False
                title = None
                text = ""
                element.clear()

    # print(postings)
    for i in range(0,8):
        save(i)
    for i in range(0, 8):
        merge(i)
    print("TIME:", (time.time() - start_time)/60, "Minutes")
    print("Total Tokens:", total_tokens)
    print("Index tokens:", index_tokens)
    print("Index tokens2:", index_tokens2)
    # stat_f = open(stat_path,"w")
    # stat_f.write(str(total_tokens) + "\n")
    # stat_f.write(str(index_tokens))
    # stat_f.close()

if __name__ == "__main__":
    main()