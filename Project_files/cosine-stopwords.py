import os
import sys
import glob
import math
import xlsxwriter
import sys

dict_by_word = {}
term_freq_dict = {}
term_dict = {}
term_doc_id = {}
cosine_term_wise_docfq = {}
cosine_doc_wise_term = {}
dict_by_word_query = {}
wordset_query = set()
word_list = []
wordset = set() # list of unique terms
univeral_wordset = set()
dict_by_word_docid = {} # main data-structure to create the inverted index stored in the format of Doctionary where
                        # each value of the dictionary is again a list of dictionary.
                        # the key of the main dictionary is the term and its value contains another dictionary where 
                        # each key is the doc-id and its value is the frequency for the term for that particular docid.

def store_in_dictionary(word):
	global wordset
	global dict_by_word
	if(word not in wordset):
		wordset.add(word)
		dict_by_word[word] = 1
	else:
		dict_by_word[word] =  dict_by_word[word] + 1


def store_in_dictionary_query(word):
	global wordset_query
	global dict_by_word_query
	if(word not in wordset_query):
		wordset_query.add(word)
		dict_by_word_query[word] = 1
	else:
		dict_by_word_query[word] =  dict_by_word_query[word] + 1


def get_stopwords():
	hand = open("common_words")
	set_of_word = set()
	for line in hand:
		line = line.rstrip()
		set_of_word.add(line)
	return(set_of_word)


def create_index():
	global TOTAL_DOCUMENT
	global dict_by_word_docid
	global cosine_doc_wise_term
	global term_docid_table
	global term_doc_id
	global wordset
	global univeral_wordset
	global dict_docid_length
	global doc_wise_term_index
	global dict_by_word
	global map_docid
	map_docid = {}
	dict_docid_length = {}
	term_docid_table = {} # store filename with doc id
	list_per_doc = {}
	doc_wise_term_index = {}
	dict_by_word1 = {}
	global doc_length
	doc_length = 0
	count = 0
	TOTAL_DOCUMENT = 0
	stop_words = get_stopwords()
	for i in glob.glob("cacm_corpus/*.html"): #parsed files are stored in this folder.
		i = i.rsplit(os.sep,1)[1]
		print(i)
		count = count + 1
		#if (count == 5): break
		filename = i
		TOTAL_DOCUMENT = TOTAL_DOCUMENT + 1
		term_docid_table[str(count)] = i
		map_docid[i] = str(count)
		hand = open("cacm_corpus/" + filename)
		docid = filename.rsplit('.',1)[0]
		token_count = 0
		dict_by_word = {}
		dict_word = {}
		for line in hand:
			line = line.rstrip()

			if(line not in stop_words):
				token_count = token_count +  1
				doc_length = doc_length + 1
				store_in_dictionary(line)

		dict_docid_length[str(count)] = token_count

		doc_wise_term_index[str(count)] = dict_by_word
		for key, value in dict_by_word.iteritems():
			dict_by_word1[key] = float(float(value)/float(token_count))
			# Tf value for each term in the Document ID

		cosine_doc_wise_term[str(count)] = dict_by_word1 # normalized Tf value for each term in the Document ID which will
														 # be used in creating the Cosine Value.
		hand = open("cacm_corpus/" + filename)
		# merging the newly found and old term-frequenncy with docid.
		for line1 in wordset:
			if line1 not in univeral_wordset:
				univeral_wordset.add(line1)
				list_per_doc[str(count)] = dict_by_word[line1]
				list1 = [list_per_doc]
				term_doc_id[line1] = [str(count)]
				dict_by_word_docid[line1] = list1[:]
			else:
				list_per_doc[str(count)] = dict_by_word[line1]
				term_doc_id[line1].append(str(count))
				dict_by_word_docid[line1].append(list_per_doc)
			list_per_doc = {}
		wordset = set()
		dict_by_word = {}
		list_per_doc = {}
		dict_by_word1 = {}

def create_BM25(TOTAL_DOCUMENT,dict_by_word_docid,term_doc_id,doc_wise_term_index,K,dict_by_word_query,dict_info_rel):
	k1 = 2.0
	k2 = 5.0
	b = 0.375
	bm25 = {}
	R = dict_info_rel['R']
	r_dict = dict_info_rel['r']

	for docid_key, term_freq_doc_wise in doc_wise_term_index.iteritems():

		sum_query_term = 0
		for quert_term, query_freq in dict_by_word_query.iteritems():
			ni=0
			fi=0
			try:
				lst_dict_docid = dict_by_word_docid[quert_term]
				ni = len(lst_dict_docid)
			except KeyError as e:
				ni = 0
			try:
				fi = term_freq_doc_wise[quert_term]
			except KeyError as e:
				fi = 0

			first_term_num = float(r_dict[quert_term] + 0.5)/float(R - r_dict[quert_term] + 0.5)
			first_term_den = float(ni - r_dict[quert_term]+0.5)/ float(TOTAL_DOCUMENT - ni - R + r_dict[quert_term] + 0.5 ) 
			first_term = float( first_term_num / first_term_den)
			second_term = float(float(float(k1 + 1.0) * float(fi)) / float(float(K[docid_key]) + float(fi)))
			third_term =  float(float(float(k2 + 1.0) * float(query_freq)) / float(float(k2) + float(query_freq)))


			sum_query_term = sum_query_term + float(float(math.log(first_term)) * float(third_term) * float(second_term))

		bm25[docid_key] = sum_query_term

	return bm25



def create_model():
	global TOTAL_DOCUMENT
	global doc_length
	global dict_by_word
	global cosine_doc_wise_term
	global wordset
	global univeral_wordset
	global dict_by_word_docid
	global term_doc_id
	global term_docid_table
	global dict_docid_length
	global doc_wise_term_index
	global dict_by_word_query
	global map_docid
	global wordset_query
	create_index()
	#dict_by_word_docid is the Inverted Index whose formation is finished here.
	print(doc_length)
	av_dl = float(float(doc_length)/float(TOTAL_DOCUMENT))
	print(TOTAL_DOCUMENT)
	print(av_dl)

	bm25 = {}
	k1 = 1.2
	k2 = 0
	b = 0.5
 	K = {}
	for key, value in dict_docid_length.iteritems():
		K[key] = k1 * ((1-b) + (b * (value/av_dl)))


	for key, listvalue in dict_by_word_docid.iteritems(): 
		total = 0
		doc_count = 0
		for lst in term_doc_id[key]:
			doc_count = doc_count + 1
		cosine_term_wise_docfq[key] = float(1 + float(math.log(float(TOTAL_DOCUMENT)/float(doc_count))))
		#cosine_term_wise_docfq is the idf value of each term in the Inverted List Index


	value_doc_id = {}
	den_value_doc_id = {}
	stop = 0
	for docID, tf_value in cosine_doc_wise_term.iteritems():
		stop = stop + 1;
		initial_value = 0
		dict_by_word_for_tf = tf_value
		for key, value in dict_by_word_for_tf.iteritems():
			value_doc_id[key] = float(value) * float(cosine_term_wise_docfq[key])
			den_square = float(float(value_doc_id[key]) * float(value_doc_id[key]))
			initial_value = initial_value + den_square
		den_value_doc_id[docID] = initial_value
		#den_value_doc_id is the tf * idf of each term in all the Documents.

	hand = open("cacm.rel")
	query_count_list = []
	relevant_doc_dict = {}

	for line in hand:
		line = line.rstrip()
		linelist = line.split(" ")
		query_count = linelist[0]
		doc_id = linelist[2] + ".html"
		if query_count not in query_count_list:
			doc_key = query_count
			query_count_list.append(query_count)
			list1 = [doc_id]
			relevant_doc_dict[doc_key] = list1[:]

		else:
			relevant_doc_dict[doc_key].append(doc_id)
	list1 = []



	hand = open("query_cacm.txt") #"query.txt" is the text file conating the queries.
	QueryList=[]


	argument_list = sys.argv
	argument = argument_list[1]

	if argument == "1":
		if not os.path.exists("Output"):
			os.makedirs("Output")
		workbook = xlsxwriter.Workbook('Output/tfidf_retrieval_cacm' + '.xlsx')
	elif argument == "2":
		if not os.path.exists("Output"):
			os.makedirs("Output")
		workbook = xlsxwriter.Workbook('Output/cosine_retrieval_stop_cacm' + '.xlsx')
	elif argument == "3":
		if not os.path.exists("Output"):
			os.makedirs("Output")
		workbook = xlsxwriter.Workbook('Output/bm25_retrieval_cacm' + '.xlsx')
	else:
		print('Enter Correct Argument')

	stop_words = get_stopwords()

	print("Query-by-query-Analysis")
	for line in hand:
		# processing one query at a time.
		linelist = line.split(" ",1)
		queryid = linelist[0]
		QueryList = linelist[1]

		Query = []
		QueryList = QueryList.split()
		for q1 in QueryList:
			if(q1 not in stop_words):
				Query.append(q1)

		tf_idf_doc_inner = {}
		tf_idf_doc = {}
		Document_present = []

		print(queryid + "starts")

		dict_info_rel = {}

		try:
			doc_list = relevant_doc_dict[queryid]

			dict_info_rel['R'] = len(doc_list)
			ri_count = 0
			ri_term = {}
			for q in Query:
				for doc in doc_list:
					digit = doc.split('.')[0].split('-')[1]
					if len(digit) < 4:
						for i in range(4-len(digit)):
							digit = '0' + digit

					doc = doc.split('-')[0]+'-'+digit+'.html'		
					doc_id_num = map_docid[doc]
					dict_terms = doc_wise_term_index[doc_id_num]
					terms = dict_terms.keys()
					if q in terms:
						ri_count = ri_count + 1
				ri_term[q] = ri_count
				ri_count = 0

			dict_info_rel['r'] = ri_term
		except:
			dict_info_rel['R'] = 0
			ri_term = {}
			for q in Query:
				ri_term[q] = 0
			dict_info_rel['r'] = ri_term


		for q in Query:
			total_terms = dict_by_word_docid.keys()
			if q in total_terms:
				list_value = dict_by_word_docid[q]
				for lst in list_value:
					for key, value in lst.iteritems():
						try:
							df = float(cosine_term_wise_docfq[q])
							terms_for_docid = cosine_doc_wise_term[key]
							tf = float(terms_for_docid[q])
							tf_idf_doc_inner[key] = float(df * tf)
							Document_present.append(key)
						except KeyError as e:
							tf_idf_doc_inner[key] = float(0)
				
				for interger_key, value_doc_name in term_docid_table.iteritems():
					if interger_key not in Document_present:
						tf_idf_doc_inner[interger_key] = 0
				tf_idf_doc[q] = tf_idf_doc_inner
				Document_present = []
				tf_idf_doc_inner = {}

		#tf_idf_doc contains the tf * idf for each term in the query
		global dict_by_word_query

		query_length = len(Query)
		dict_by_word_query = {}
		wordset_query = set()
		for q in Query:
			store_in_dictionary_query(q) 
			# tf for the Query Terms
		dict_by_word_query_bm = {}

		dict_by_word_query_bm = dict_by_word_query
		for key, value in dict_by_word_query.iteritems():
			dict_by_word_query[key] = float(float(value)/float(query_length))
			#normalized tf for the Query Terms

		Document_present = []
		tf_idf_query_inner = {}
		tf_idf_query = {}
		bm25 = create_BM25(TOTAL_DOCUMENT,dict_by_word_docid,term_doc_id,doc_wise_term_index,K,dict_by_word_query_bm,dict_info_rel)

		dict_by_word_query_bm = {}


		for q in Query:
			try:
				tf_query = dict_by_word_query[q]
				df_query = float(cosine_term_wise_docfq[q])
				tf_idf_query[q] = float(df_query * tf_query)
			except KeyError as e:
				tf_idf_query[q] = 0

		#tf_idf_query contains the tf * idf of each query-term
		final_tf_idf_by_doc = {}
		current_doc_processedd = 0
		final_cosine_by_doc = {}
		while (current_doc_processedd <=  (TOTAL_DOCUMENT - 1)):
			current_doc_processedd = current_doc_processedd + 1
			cosine_den_2term_add = 0.0
			cosine_num_addition = 0.0
			cosine_den_1term_add = 0.0
			for q in Query:
				try:
					dictionary_for_doc = tf_idf_doc[q]
					cosine_num_1term = float(dictionary_for_doc[str(current_doc_processedd)])
				except:
					cosine_num_1term = 0
				try:
					cosine_num_2term = float(tf_idf_query[q])
				except:
					cosine_num_2term = 0
				cosine_num_mult = float(cosine_num_1term * cosine_num_2term)
				cosine_den_1term = float(cosine_num_1term * cosine_num_1term)
				cosine_den_2term = float(cosine_num_2term * cosine_num_2term)
				cosine_num_addition = float(float(cosine_num_addition) + float(cosine_num_mult))
				cosine_den_1term_add = float(float(cosine_den_1term_add) + float(cosine_den_1term))
				cosine_den_2term_add = float(float(cosine_den_2term_add) + float(cosine_den_2term))
			try:
				final_cosine_by_doc[str(current_doc_processedd)] = float(float(cosine_num_addition)/float(math.sqrt(den_value_doc_id[str(current_doc_processedd)]) * math.sqrt(cosine_den_2term_add)))
				final_tf_idf_by_doc[str(current_doc_processedd)] = float(cosine_num_addition)
			except ZeroDivisionError as e:
				final_cosine_by_doc[str(current_doc_processedd)] = 0
				final_tf_idf_by_doc[str(current_doc_processedd)] = 0

		dict_by_word_query = {}


		

		worksheet = workbook.add_worksheet(str(queryid))
		if argument == "1":
			saveToWorksheet(worksheet,final_tf_idf_by_doc,queryid,term_docid_table,"TF-IDF")
		elif argument == "2":
			saveToWorksheet(worksheet,final_cosine_by_doc,queryid,term_docid_table,"Cosine")
		elif argument == "3":
			saveToWorksheet(worksheet,bm25,queryid,term_docid_table,"bm-25")
		else:
			print('Enter Correct Argument')

		print(queryid + "ends")

	workbook.close()


def saveToWorksheet(worksheet,final_dict,queryid,term_docid_table,system):
	row = 0
	col = 0
	count = 0
	for entry in sorted(final_dict.items(), key = lambda x: x[1], reverse=True):
		count = count + 1
		if (count == 101): break
		worksheet.write(row,col,queryid)
		worksheet.write(row,col+1,"Q0")
		worksheet.write(row,col+2,term_docid_table[str(entry[0])])
		worksheet.write(row,col+3,count)
		worksheet.write(row,col+4,str(round(entry[1], 8)))
		worksheet.write(row,col+5,system)
		row = row + 1

if __name__ == "__main__":
	create_model()
	