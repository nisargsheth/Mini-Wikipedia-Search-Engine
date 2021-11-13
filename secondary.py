import pickle
import time
import os

################################################################################################
############################# SECONDARY INDEX MAKER ##########################################
if(not os.path.exists("sec_inverted_index")):
    os.makedirs("sec_inverted_index")

for i in range(0, 26):
    letter = chr(i + 97)
    print("Letter: ", letter)
    st = time.time()
    f = open("inverted_index/" + letter, "r")
    if(not os.path.exists("sec_inverted_index/" + letter)):
        os.makedirs("sec_inverted_index/" + letter)
    f0 = open("sec_inverted_index/" + letter + "/" + letter + "0", "w")
    fn = open("sec_inverted_index/" + letter + "/" + letter + "#", "w")
    f_ptrs = []
    for j in range(0,26):
        letter_j = chr(j + 97)
        f_ptrs.append(open("sec_inverted_index/" + letter + "/"+ letter + letter_j, "w"))
    line = f.readline()
    while(line):
        word = line.split(':')[0]
        if(len(word)<2):
            f0.write(line)
        else:
            if(ord(word[1])<97):
                fn.write(line)
            else:
                f_ptrs[ord(word[1]) - 97].write(line)
        line = f.readline()
    print(time.time() - st, "seconds")

if(not os.path.exists("sec_inverted_index/#")):
    os.makedirs("sec_inverted_index/#")
f = open("inverted_index/#", "r")
f_ptrs = []
for i in range(0, 10):
    f_ptrs.append(open("sec_inverted_index/#/" + chr(48+i), "w"))

line = f.readline()
while(line):
    f_ptrs[ord(line[0])-48].write(line)
    line = f.readline()

