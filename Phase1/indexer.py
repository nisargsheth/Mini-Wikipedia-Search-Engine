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

wiki_dump_path = sys.argv[1]

if(not os.path.exists(os.path.dirname(wiki_dump_path))):
    os.makedirs(os.path.dirname(wiki_dump_path))

inverted_index_path = sys.argv[2] + "/index.txt"

if(not os.path.exists(os.path.dirname(inverted_index_path))):
    os.makedirs(os.path.dirname(inverted_index_path))

stat_path = sys.argv[3]

postings = {}
text = ""
title = None
id = None
in_revision = False
in_page = False
page_id=1
file_id=0
pages_per_file=20000
total_tokens=0
index_tokens=0
field_to_index = {'t':0, 'b':1, 'c':2, 'i':3, 'r':4, 'e':5}
index_to_field = {0:'t', 1:'b', 2:'c', 3:'i', 4:'r', 5:'e'}

stemmer = Stemmer.Stemmer("english")
STOP_WORDS = set(['whence', 'here', 'show', 'were', 'why', 'n’t', 'the', 'whereupon', 'not', 'more', 'how', 'eight', 'indeed', 'i', 'only', 'via', 'nine', 're', 'themselves', 'almost', 'to', 'already', 'front', 'least', 'becomes', 'thereby', 'doing', 'her', 'together', 'be', 'often', 'then', 'quite', 'less', 'many', 'they', 'ourselves', 'take', 'its', 'yours', 'each', 'would', 'may', 'namely', 'do', 'whose', 'whether', 'side', 'both', 'what', 'between', 'toward', 'our', 'whereby', "'m", 'formerly', 'myself', 'had', 'really', 'call', 'keep', "'re", 'hereupon', 'can', 'their', 'eleven', '’m', 'even', 'around', 'twenty', 'mostly', 'did', 'at', 'an', 'seems', 'serious', 'against', "n't", 'except', 'has', 'five', 'he', 'last', '‘ve', 'because', 'we', 'himself', 'yet', 'something', 'somehow', '‘m', 'towards', 'his', 'six', 'anywhere', 'us', '‘d', 'thru', 'thus', 'which', 'everything', 'become', 'herein', 'one', 'in', 'although', 'sometime', 'give', 'cannot', 'besides', 'across', 'noone', 'ever', 'that', 'over', 'among', 'during', 'however', 'when', 'sometimes', 'still', 'seemed', 'get', "'ve", 'him', 'with', 'part', 'beyond', 'everyone', 'same', 'this', 'latterly', 'no', 'regarding', 'elsewhere', 'others', 'moreover', 'else', 'back', 'alone', 'somewhere', 'are', 'will', 'beforehand', 'ten', 'very', 'most', 'three', 'former', '’re', 'otherwise', 'several', 'also', 'whatever', 'am', 'becoming', 'beside', '’s', 'nothing', 'some', 'since', 'thence', 'anyway', 'out', 'up', 'well', 'it', 'various', 'four', 'top', '‘s', 'than', 'under', 'might', 'could', 'by', 'too', 'and', 'whom', '‘ll', 'say', 'therefore', "'s", 'other', 'throughout', 'became', 'your', 'put', 'per', "'ll", 'fifteen', 'must', 'before', 'whenever', 'anyone', 'without', 'does', 'was', 'where', 'thereafter', "'d", 'another', 'yourselves', 'n‘t', 'see', 'go', 'wherever', 'just', 'seeming', 'hence', 'full', 'whereafter', 'bottom', 'whole', 'own', 'empty', 'due', 'behind', 'while', 'onto', 'wherein', 'off', 'again', 'a', 'two', 'above', 'therein', 'sixty', 'those', 'whereas', 'using', 'latter', 'used', 'my', 'herself', 'hers', 'or', 'neither', 'forty', 'thereupon', 'now', 'after', 'yourself', 'whither', 'rather', 'once', 'from', 'until', 'anything', 'few', 'into', 'such', 'being', 'make', 'mine', 'please', 'along', 'hundred', 'should', 'below', 'third', 'unless', 'upon', 'perhaps', 'ours', 'but', 'never', 'whoever', 'fifty', 'any', 'all', 'nobody', 'there', 'have', 'anyhow', 'of', 'seem', 'down', 'is', 'every', '’ll', 'much', 'none', 'further', 'me', 'who', 'nevertheless', 'about', 'everywhere', 'name', 'enough', '’d', 'next', 'meanwhile', 'though', 'through', 'on', 'first', 'been', 'hereby', 'if', 'move', 'so', 'either', 'amongst', 'for', 'twelve', 'nor', 'she', 'always', 'these', 'as', '’ve', 'amount', '‘re', 'someone', 'afterwards', 'you', 'nowhere', 'itself', 'done', 'hereafter', 'within', 'made', 'ca', 'them'])

def get_tokens(text):
    if(text is None or len(text)==0):
        return []
    tokens = re.split(r'[^A-Za-z0-9]+', text)
    return tokens

def index_field(field, content):
    field_index = field_to_index[field]
    field_tokens = get_tokens(content)
    for field_token in field_tokens:
        if(field_token in STOP_WORDS):
            continue
        field_token = stemmer.stemWord(field_token)
        if(field_token in postings):
            if(page_id not in postings[field_token]):
                postings[field_token][page_id] = [0,0,0,0,0,0]
        else:
            postings[field_token] = {}
            postings[field_token][page_id] = [0,0,0,0,0,0]
        postings[field_token][page_id][field_index] += 1



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

def save():
    f = open(str(file_id), "w")
    for word in sorted(postings.keys()):
        line=word+":"
        for page in postings[word]:
            line += "d"+str(page)+"-"
            field_counts = postings[word][page]
            for i,count in enumerate(field_counts):
                if(count):
                    line += index_to_field[i]+str(count)+","
            line += "|"
        line += "\n"
        f.write(line)
    f.close()


class DataWrap:
    def __init__(self, data):
        self.data = data  
    def __lt__(self, other):
        return self.data[0].split(':')[0] < other.data[0].split(':')[0]

def merge():
    global index_tokens
    prev = ""
    file_handles = []
    heap = []
    sorted_file = open(inverted_index_path,"w")

    for i in range(0,file_id+1):
        file_handles.append(open(str(i),"r"))
        file_handles[i].readline()
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
                if(page_id % pages_per_file==0):
                    save()
                    file_id += 1
                    postings = {}
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

    # print(postings)
    save()
    merge()
    stat_f = open(stat_path,"w")
    stat_f.write(str(total_tokens) + "\n")
    stat_f.write(str(index_tokens))
    stat_f.close()

if __name__ == "__main__":
    main()
