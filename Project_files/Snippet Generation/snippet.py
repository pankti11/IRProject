import sys
from itertools import izip
import string
import os


PREFERRED_SNIPPET_LENGTH = 60
MAX_SNIPPET_LENGTH = 80
SNIPPET_MATCH_WINDOW_SIZE = 5

class bcolors:
    OKBLUE = '\033[94m'
    ENDC = '\033[0m'

opening = '''<span style="color: red; font-family: 'Liberation Sans',sans-serif">'''
closing = '''</span>'''


def get_relevant_docs_by_query(fileName):
    rel_docs = {}
    docs = []

    with open(fileName) as f:
        content = f.readlines()

    q_no = int(content[0].split()[0])

    for line in content:
        new_q_no = int(line.split()[0])

        if q_no == new_q_no:
            docs.append(line.split()[1])
        else:
            rel_docs[q_no] = docs
            docs = []
            docs.append(line.split()[1])
            q_no = new_q_no

    rel_docs[q_no] = docs

    return rel_docs

def get_query_expansion(fName):
    query={}
    with open(fName) as f:
        content = f.readlines()
    for line in content:
        q_line = line.split()
        query[q_line[0]] = ' '.join(q_line[1:])

    return query

def get_docs(fileName):
    with open(os.path.join('cacm_raw',fileName)) as f:
        content = f.readlines()

    return '\n'.join(content)


def normalize_term(term):
    return term.strip(string.punctuation).lower()


def get_normalized_terms(query):
    terms = [normalize_term(term) for term in query.split()]

    return terms


def list_range(x):
    return max(x) - min(x)


def get_window(positions, indices):

    return [word_positions[index] for word_positions, index in \
            izip(positions, indices)]


def get_min_index(positions, window):
    min_indices = (window.index(i) for i in sorted(window))
    for min_index in min_indices:
        if window[min_index] < positions[min_index][-1]:
            return min_index

def create_sentences(doc):
    doc_dict = {}
    doc_sentences = doc.split('.')
    word_count  = 0
    for i in range(len(doc.split('.'))):
        sen_list = []
        for word in doc_sentences[i].split():
            sen_list.append(word_count)
            word_count+=1
        doc_dict[i] = sen_list

    return  doc_dict





def get_shortest_span(positions,doc):
    doc_dict = create_sentences(doc)
    pos_list = []
    max = 0
    min = 0
    for pos in positions:
        p = set(pos) & set()
        print(len(p))

    pos_list=sorted(pos_list)

    #get largest range which contains all words and does not violate range limits

def get_shortest_term_span(positions):
    # Initialize our list of lists where each list corresponds to the
    # locations within the document for a term
    indices = [0] * len(positions)
    min_window = window = get_window(positions, indices)


    # Iteratively moving the minimum index forward finds us our
    # minimum span
    while True:

        min_index = get_min_index(positions, window)
        if min_index == None:
            return min_window

        indices[min_index] += 1

        window = get_window(positions, indices)
        if list_range(min_window) > list_range(window):
            min_window = window

        if list_range(min_window) == len(positions):
            return min_window



def generate_term_positions(doc, query):
    terms = query.split()
    positions = [[] for j in range(len(terms))]
    for i, word in enumerate(doc.split()):
        for term in terms:
            if normalize_term(word) in get_normalized_terms(term):
                positions[terms.index(term)].append(i)
                break

    # Sometimes a term doesn't appear at all in the returned document
    # Remove the location list for any terms that has no locations within
    # the document
    positions = [x for x in positions if x]

    return positions


def shorten_snippet(doc, query):
    flattened_snippet_words = []
    normalized_terms = get_normalized_terms(query)

    last_term_appearence = 0
    skipping_words = False

    for i, word in enumerate(doc.split()):

        if word in normalized_terms:
            last_term_appearence = i
            skipping_words = False

        # If it's been too long since our last match, start dropping words
        if i - last_term_appearence > SNIPPET_MATCH_WINDOW_SIZE:

            # Only want to add "..." once between terms, so check our state flag first
            if not skipping_words:
                flattened_snippet_words.append("...")
                skipping_words = True

            continue

        flattened_snippet_words.append(word)

        if  len(flattened_snippet_words) > PREFERRED_SNIPPET_LENGTH:
            flattened_snippet_words=flattened_snippet_words[0:PREFERRED_SNIPPET_LENGTH]

    return ' '.join(flattened_snippet_words)


def highlight_query_terms(doc,
                          query,
                          highlight_start= bcolors.OKBLUE,
                          highlight_end=bcolors.ENDC):

    normalized_terms = get_normalized_terms(query)

    highlight_spans = []
    document_words = doc.split()

    start_span = None

    for i, word in enumerate(document_words):

        if normalize_term(word) in get_normalized_terms(query):
            if start_span is None:
                start_span = i
        else:
            if start_span is not None:
                highlight_spans.append((start_span, i - 1))
                start_span = None

    if start_span is not None:
        highlight_spans.append((start_span, i))

    for span in highlight_spans:
        document_words[span[0]] = highlight_start + document_words[span[0]]
        document_words[span[1]] = document_words[span[1]] + highlight_end

    return ' '.join(document_words)



def create_html_highlight_terms(doc,query):
    return highlight_query_terms(doc,query,opening,closing)



def highlight_doc_shortest_span(doc, query, expansion_string,html=False,max_length=PREFERRED_SNIPPET_LENGTH):
    initial_query = query
    query = query + ' ' + expansion_string
    #print query
    query = ' '.join(set(query.split()))
    #print query
    positions = generate_term_positions(doc, query)

    doc= ' '.join(doc.split())
    if not positions:
        return highlight_query_terms(' '.join(doc.split()[0: max_length]).strip(), query)

    span = get_shortest_term_span(positions)
    doc_dict = create_sentences(doc)
    doc_dict_value = {}
    for key,value in doc_dict.iteritems():
        doc_dict_value[key] = len(set(value) & set(span))

    doc_id_list = list(reversed(sorted(doc_dict_value, key=doc_dict_value.get)))[0:2]
    doc_val = doc.split('.')
    sentence_list = []
    for doc_id in doc_id_list:
        sentence_list.append(doc_val[doc_id])


    sentence_final = ' '.join(sentence_list)


    span = sorted(span)
    start = max(0, span[0] - (PREFERRED_SNIPPET_LENGTH / 2))
    end = min(len(doc.split()), span[len(positions) - 1] + (PREFERRED_SNIPPET_LENGTH / 2))
    if start > end:
        temp = start
        start = end
        end = temp

    snippet = ' '.join(doc.split()[start:end + 1])

    if (end - start > MAX_SNIPPET_LENGTH):
        snippet = shorten_snippet(snippet, query)

    if html:
        return create_html_highlight_terms(snippet.strip(), query)
    else:
        return highlight_query_terms(snippet.strip(), query)






def main():

    f = open('snippet.html', 'w')
    relevant_docs = get_relevant_docs_by_query('snippet-format.txt')
    queries  = get_query_expansion('query1.txt')
    expansion_terms = get_query_expansion('expanded-words.txt')
    for key, value in relevant_docs.iteritems():
        query = queries[str(key)]
        expansion_term  = expansion_terms[str(key)]
        k = '<p> --------------------------------------------------- </p>'
        query_ht = '<p> Query :  ' + query + ' </p> '
        #query =  'I\'m interested in mechanisms for communicating between disjoint processes, possibly, but not exclusively, in a distributed environment. I would rather see descriptions of complete mechanisms, with or without implementations, as opposed to theoretical work on the abstract problem. Remote procedure calls and message-passing are examples of my interests.'
        f.write(k + query_ht + k)
        for doc in value:
            doc_str = get_docs(doc)
            #doc_str = get_docs('CACM-3128.html')
            #expansion_term = 'proceedings oden'
            t = highlight_doc_shortest_span(doc_str, query, expansion_term)
            print t
            ht = highlight_doc_shortest_span(doc_str, query,expansion_term,True)
            doc_ht = '<p> Document Name  : ' + doc + ' </p>'
            ht = '<p>' + doc_ht + ht + '</p>' +\
                 '<p> --------------------------------------------------- </p>'


            f.write(ht)


    f.close()

if __name__ == "__main__":
    main()