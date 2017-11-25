# coding: utf-8
from bs4 import BeautifulSoup
import string
import re
import os
fileNo = 1
DIR1 = './cacm'
corpusSize = len([name for name in os.listdir(DIR1) if os.path.isfile(os.path.join(DIR1, name))])
pat = re.compile(r"([a-zA-Z]+)([,.:%$#@!=<>)(/\\?]+)([a-zA-Z]+)")
for name in os.listdir(DIR1):
    print fileNo
    fileNo += 1
    f1 = open(os.path.join(DIR1, name))
    punct = set(string.punctuation)
    soup = BeautifulSoup(f1, 'html.parser')
    DIR2 = './cacm1'
    if not os.path.exists(DIR2):
        os.mkdir(DIR2)
    f2 = open(os.path.join(DIR2, name), 'w')
    str1 = soup.find('pre').get_text()
    str1 = re.sub("[^\\x00-\\x7F]", "", str1)
    
    word_lst = []
    str2 = '\n'.join(word.strip(string.punctuation) for word in str1.split())
    str3 = re.sub(pat, r'\1\n\3', str2)
    url_less_string = re.sub(
        r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))''',
        '', str3)
    f2.write(url_less_string.lower())
    f2.close()
    f1.close()

