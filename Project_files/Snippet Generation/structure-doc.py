import re

with open('cacm.query') as oldfile, open('cacm_intermediate.query', 'w') as newfile:
    newfile.write('<root>')
    for line in oldfile:
        match = re.search('(<DOCNO>) \d+ (</DOCNO>)', line)
        if match:
            print line
        if not match:
            newfile.write(line)
    newfile.write('</root>')