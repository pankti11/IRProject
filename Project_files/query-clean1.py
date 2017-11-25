import xml.etree.ElementTree as ET
import re
with open('cacm.query') as oldfile, open('cacm_intermediate.query', 'w') as newfile:
    newfile.write('<ROOT>\n')
    for line in oldfile:
        match = re.search('(<DOCNO>) \d+ (</DOCNO>)', line)
        if match:
            print line
        if not match:
            newfile.write(line)
    newfile.write("</ROOT>")


xml = open("cacm_intermediate.query").read()
count = 0
f2 = open("query1.txt", 'w')
for child in ET.fromstring(xml):
	count = count + 1
	a = child.text
	a = a.strip()
	mystring = a.replace('\n', ' ').replace('\r', '')
	mystring = re.sub(' +',' ',mystring)
	f2.write(str(count) + " " + mystring + "\n")