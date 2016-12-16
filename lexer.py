import unicodedata
import sys
import copy
import json
import re
import codecs
import ctypes

#utf-8-sig
#f = codecs.open(A , B, "utf-8")

if len(sys.argv)<3:
	print 'usage: lexer.py input.html input.txt'
	sys.exit()

	
fhtml = open(sys.argv[1],"rb")
html = fhtml.read()

ftxt = open(sys.argv[2],"rb")

bt = "BookmarkTitle:"
bl = "BookmarkLevel:" 
bp = "BookmarkPageNumber:" 

class Title:
	title = ''
	title_level = ''
	level = 0
	page = 0
	marked = 0
	rule = ''
	def toJSON(self):
        	return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

title_array = []
cur_title = Title()

level_before = 100

progress =  "Reading TXT..."
ctypes.windll.kernel32.SetConsoleTitleA(progress)
print progress

for line in ftxt:
	if line[:len(bt)]==bt:
		ltitle = line[len(bt):].strip(' \t\n\r')
		title = re.search(u'([0-9\.\s]*)(.*)', ltitle, re.UNICODE)
		if title:			
			cur_title.title = title.group(2).strip(' \t\n\r')
			cur_title.title_level = title.group(1).strip(' \t\n\r')
		else:
			cur_title.title = ltitle
	if line[:len(bl)]==bl:
		cur_title.level = int(line[len(bl):].strip(' \t\n\r'))
	if line[:len(bp)]==bp:
		cur_title.page = int(line[len(bp):].strip(' \t\n\r'))

		cur_title.marked = 0
		if cur_title.level<level_before: #[RULE1]
			cur_title.rule = "[RULE1]"
			cur_title.marked = 1  #mark current
		if cur_title.level>level_before: #[RULE2]
			if len(title_array)>0:
				title_array[-1].rule = "[RULE2]"
				title_array[-1].marked = 1 #mark previous

		level_before = cur_title.level
		title_array.append(cur_title)
		cur_title = Title()

#for item in title_array:
#	print item.toJSON()

#<P class="p24 ft17"> HEADER </P>
if len(title_array)==0:
	print 'No titles in '+sys.argv[2]
	sys.exit()
	
progress = "PARSING HTML..."
ctypes.windll.kernel32.SetConsoleTitleA(progress)
print progress

# [RULE3]
#set h1
last_h1_page = title_array[0].page
#print "searching: "+title_array[0].title

def replaceHeader(html, header, page, h):
	print "page = "+str(page)
	fheader = re.finditer(r"<[\s]*div[\s]*id[\s]*=[\s]*\"page_"+str(page)+r"\"[\s]*>[\s\S]*?(<[\s]*[pP].*?"+re.escape(header)+r"[\s\S]*?<[\s]*/[\s]*[pP][\s]*>)", html,re.UNICODE | re.IGNORECASE)
	for m in fheader:
		#print "header: "+str(m.start(0))+" end: "+str(m.end(0))
		st = html[m.start(1) : m.end(1)]
		print st
		new_str = re.sub(r"<[\s]*/[\s]*[pP][\s]*>$", "</"+h+">", st)  #end
		new_str = re.sub(r"<[\s]*[pP]", "<"+h, new_str)  #first
		print new_str	
		return re.sub(re.escape(st),new_str,html)
	return html 

html2 = replaceHeader(html, title_array[0].title, title_array[0].page, "h1")

progress = "PARSING HTML... 1%"
ctypes.windll.kernel32.SetConsoleTitleA(progress)
print progress
num = 1;
total = len(title_array)
for titles in title_array[1:]:
	num=num+1
	if num%2 == 0:
		progress = "PARSING HTML... "+str(int(num*100/total))+"%"
		ctypes.windll.kernel32.SetConsoleTitleA(progress)
		print progress
	
	if titles.marked == 1:
		if last_h1_page==titles.page:
			html2 = replaceHeader(html2, titles.title, titles.page, "h2")	# [RULE4]
		if last_h1_page<>titles.page:
			html2 = replaceHeader(html2, titles.title, titles.page, "h1")	# [RULE5]
			last_h1_page = titles.page
	if titles.marked == 0:
		if titles.page-last_h1_page<3:
			html2 = replaceHeader(html2, titles.title, titles.page, "h2")	# [RULE6]
		else:
			html2 = replaceHeader(html2, titles.title, titles.page, "h1")	# [RULE7]
			last_h1_page = titles.page
	
fnew = open(sys.argv[1]+".new.html", "wb")
fnew.write(html2)
fnew.close()

ctypes.windll.kernel32.SetConsoleTitleA("PARSING HTML... DONE")
print "FILE  "+sys.argv[1]+".new.html   CREATED SUCCESSFULLY"

#print html
