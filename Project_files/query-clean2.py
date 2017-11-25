# coding: utf-8
import regex as re
import string
hand = open("query1.txt")
pat = re.compile(r"([a-zA-Z]+)([+*?,.:%$#@!=<>()/\\]+)([*+-?,.:%$#@!=<>()/\\]*)([a-zA-Z0-9]+)")
pat1 = re.compile(r"([a-zA-Z]+)([']+)([a-zA-Z0-9]+)")
f2 = open("query_cacm.txt", 'w')
for line in hand:
	punct = set(string.punctuation)
	str1 = re.sub("[^\\x00-\\x7F]", "", line)
	word_lst = []
	str2 = ' '.join(word.strip(string.punctuation) for word in str1.split())
	str3 = re.sub(pat, r'\1 \4', str2)	
	str4 = re.sub(pat1,r'\1\3',str3)
	url_less_string = re.sub(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))''','', str4)
	f2.write(url_less_string.lower() + "\n")

