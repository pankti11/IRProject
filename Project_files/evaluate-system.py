import xlrd
import os
import sys
import glob
import xlsxwriter
import math

def test_fn():
    if not os.path.exists("worbooks-evaluation-" + type1):
        os.makedirs("worbooks-evaluation-" + type1)

    workbook = xlsxwriter.Workbook("worbooks-evaluation-" + type1 + "/" + type1 + str(q_no) + '.xlsx')

    worksheet = workbook.add_worksheet()
    col = 0
    worksheet.write(0, col, "RANK")
    worksheet.write(0, col + 1, "REL/NON-REL")
    worksheet.write(0, col + 2, "PRECISION")
    worksheet.write(0, col + 3, "RECALL")

    row = 1

    # print "RANK"
    # print rank
    rank_init = 0
    while rank_init < rank:
        rank_init = rank_init + 1
        # print(rank_init)
        worksheet.write(row, col, str(rank_init))
        list_PR = PR_table[rank_init]
        worksheet.write(row, col + 1, str(list_PR[0]))
        worksheet.write(row, col + 2, str(list_PR[1]))
        worksheet.write(row, col + 3, str(list_PR[2]))
        row = row + 1
    workbook.close()


def getRelevanceFeedback():
    lines = tuple(open('cacm.rel', 'r'))
    q_no = int(lines[0].split()[0])
    rel_dict = {}
    rel_docs=[]
    for line in lines:
        new_q_no = int(line.split()[0])
        
        if q_no  == new_q_no:
            rel_docs.append(line.split()[2])
        else:
            #print q_no
            rel_dict[q_no] = rel_docs
            #print 'q_no '+ str(q_no) + ' : '+str(len(rel_docs))
            rel_docs=[]
            rel_docs.append(line.split()[2])
            q_no = new_q_no

    #print q_no
    rel_dict[q_no] = rel_docs 
    #print rel_docs

    return rel_dict        
                

RR =[]
AP = []
p_at_5 = []
p_at_20 = []
PR_table_list=[]
non_rel  = 0
non_rel_count = 0
#----------------------------------------------------------------------
def open_file(path,relevance_dict,filePrefix,type1):
    global non_rel_count

    """
    Open and read an Excel file
    """
    book = xlrd.open_workbook(path)
 
    # print number of sheets
 
    # print sheet names
 
    # get the first worksheet
    
    for sheet in book.sheets():    
        non_rel =0
        total_rows = sheet.nrows

        total_cols = sheet.ncols

        ret_rel_docs = [] # our retreived relevant 100 documents
        print_it = False
        for row in range(total_rows):
            cells = sheet.row_slice(rowx=row,
                                    start_colx=0,
                                    end_colx=total_cols)
        
            ret_rel_docs.append(cells[2].value.split('.')[0])
            if cells[0].value == '12' or cells[0].value == '13'  or cells[0].value == '19'  or cells[0].value == '23'  or cells[0].value == '24' or cells[0].value == '25' :
                print_it = True
            else:
                print_it = False    

        PR_table={}
        rel_till_now = 0
        q_no = int(sheet.name)

        if q_no in relevance_dict:
            total_rel = len(relevance_dict[q_no])
            #print ' q_no  ' + str(q_no) + ' total-rel ' + str(total_rel)
        else:
            total_rel = 0
            non_rel =1
            non_rel_count +=1

        #print 'total-rel   ' + str(total_rel) + '  ' + str(q_no)
        #print 'ret-rel-docs   ' + str(len(ret_rel_docs)) + '   ' + str(q_no)

        total_precision = 0.0
        first = False
        rr = 0
        for rk in range(len(ret_rel_docs)):

            rank = rk+1
            precison_recall=[]

            if total_rel != 0 :
                #print ret_rel_docs[rk] + "    " + relevance_dict[q_no][0]
                if ret_rel_docs[rk] in relevance_dict[q_no]:
                    rel_till_now = rel_till_now + 1
                    precison_recall.append('R')
                    total_precision += float(float(rel_till_now)/float(rank))
                    if not first:
                        first = True
                        rr = rank
                        #print 'rr '+str(rr)
                    
                else:
                    precison_recall.append('N')

            if total_rel  == 0 :
                precison_recall.append('N')  # Relevant info          
                precison_recall.append('0')  # precision
                precison_recall.append('0')  # recall
            else:        
                precison_recall.append(str(rel_till_now)+'/'+ str(rank) + ' = ' +str(float(float(rel_till_now)/float(rank))))
                precison_recall.append(str(rel_till_now) + '/' + str(total_rel) + ' = '+ str(float(rel_till_now/float(total_rel))))

            PR_table[rank] = precison_recall

        #print rel_till_now
        # MAP
        if rel_till_now != 0:
            AP.append(total_precision / float(rel_till_now))
            if print_it:
                print q_no
                print total_precision/ float(rel_till_now)
        else:
            AP.append(0.0)



        # MRR
        if rr != 0:
            RR.append(float(1 / float(rr)))
            if print_it:
                print 1/ float(rr)
        else:
            RR.append(0)

        p_at_5.append(PR_table[5][1])
        p_at_20.append(PR_table[20][1])
        if non_rel == 0 :
            PR_table_list.append(PR_table)
        if non_rel == 1:
            PR_table_list.append(float('nan'))

    # write it to xls sheet here.



#----------------------------------------------------------------------

def write_to_file(fName):
    # file create
    if os.path.exists(fName):
        os.mkdir(fName)
    workbook = xlsxwriter.Workbook(fName + ".xlsx")

    q_id = 0
    for table in PR_table_list:
        if type(table) is dict :
            col = 0
            row = 0
            worksheet = workbook.add_worksheet(str(q_id+1))
            worksheet.write(row, col, "RANK")
            worksheet.write(row, col + 1, "REL/NON-REL")
            worksheet.write(row, col + 2, "PRECISION")
            worksheet.write(row, col + 3, "RECALL")
            row = 1
            for rank,rel_data in table.iteritems():
                #print('DATA')
                #print(rel_data)
                worksheet.write(row,col,str(rank))
                worksheet.write(row,col+1,str(rel_data[0]))
                worksheet.write(row, col + 2, str(rel_data[1]))
                worksheet.write(row, col + 3, str(rel_data[2]))
                row = row + 1

            row = row + 2
            worksheet.write(row,col,"PR @ 5")
            worksheet.write(row, col+1, str(p_at_5[q_id]))
            row+=1
            worksheet.write(row, col, "PR @ 20")
            worksheet.write(row, col + 1, str(p_at_20[q_id]))


        q_id += 1

    workbook.close()



    # create a folder named fName
    # write an excel file in folder using PRRank dict, MAP MAR P@5 P@20



#----------------------------------------------------------------------

if __name__ == "__main__":
    relevance_dict = getRelevanceFeedback()

    workbook = xlsxwriter.Workbook("System-wise-Evaluation" + ".xlsx")

    worksheet = workbook.add_worksheet()
    row = 0
    col = 0
    worksheet.write(row,col,"SYSTEM-NAME")
    worksheet.write(row,col+1,"MAP")
    worksheet.write(row,col+2,"MRR")

    print 'tf-idf'
    count = 0
    # for i in glob.glob("Output/*.xlsx"):
    #     i = i.rsplit(os.sep,1)[1]
    #     count = count + 1
    #     #print(i)
    open_file("Output/tfidf_retrieval_cacm.xlsx",relevance_dict,'tfidf_retrieval_cacm',"tfidf")

    print 'MAP : ' + str(sum(AP)/( len(AP) - non_rel_count))
    print 'MRR : ' + str(sum(RR)/float(len(RR) - non_rel_count))

    row = row +1 
    worksheet.write(row,col,"tf-idf-evaluation")
    worksheet.write(row,col+1,str(sum(AP)/(len(AP) - non_rel_count)))
    worksheet.write(row,col+2,str(sum(RR)/float(len(RR)- non_rel_count)))

    write_to_file('tf-idf-evaluation')

    AP = []
    RR = []
    p_at_5 = []
    p_at_20 = []
    PR_table_list = []
    non_rel_count = 0



    # #bm 25
    print 'bm25'
    count = 0
    # for i in glob.glob("worbooks-bm25/*.xlsx"):
    #     i = i.rsplit(os.sep,1)[1]
    #     count = count + 1
    #     #print(i)
    open_file("Output/bm25_retrieval_cacm.xlsx",relevance_dict,'bm25_retrieval_cacm',"bm25")

    print 'MAP : ' + str(sum(AP)/(len(AP)- non_rel_count))
    print 'MRR : ' + str(sum(RR)/float(len(RR) - non_rel_count))

    row = row +1 
    worksheet.write(row,col,"bm25-evaluation")
    worksheet.write(row,col+1,str(sum(AP)/(len(AP)- non_rel_count)))
    worksheet.write(row,col+2,str(sum(RR)/float(len(RR)- non_rel_count)))


    write_to_file('bm25-evaluation')

    AP = []
    RR = []
    p_at_5 = []
    p_at_20 = []
    PR_table_list = []
    non_rel_count = 0

    # print 'bm25-version2'
    # count = 0
    # # for i in glob.glob("worbooks-bm25/*.xlsx"):
    # #     i = i.rsplit(os.sep,1)[1]
    # #     count = count + 1
    # #     #print(i)
    # open_file("Output/bm25_retrieval_cacm-version2.xlsx",relevance_dict,'bm25_retrieval_cacm-version2',"bm25-version2")

    # print 'MAP : ' + str(sum(AP)/(len(AP)- non_rel_count))
    # print 'MRR : ' + str(sum(RR)/float(len(RR) - non_rel_count))

    # row = row +1 
    # worksheet.write(row,col,"bm25-evaluation-version2")
    # worksheet.write(row,col+1,str(sum(AP)/(len(AP)- non_rel_count)))
    # worksheet.write(row,col+2,str(sum(RR)/float(len(RR)- non_rel_count)))


    # write_to_file('bm25-evaluation-version2')

    AP = []
    RR = []
    p_at_5 = []
    p_at_20 = []
    PR_table_list = []
    non_rel_count = 0

    # cosine
    print 'cosine'
    count = 0
    # for i in glob.glob("worbooks-cosine/*.xlsx"):
    #     i = i.rsplit(os.sep,1)[1]
    #     #print(i)
    #     count = count + 1
    open_file("Output/cosine_retrieval_cacm.xlsx",relevance_dict,'cosine_retrieval_cacm',"cosine")
    
    print 'MAP : ' + str(sum(AP)/(len(AP)- non_rel_count))
    print 'MRR : ' + str(sum(RR)/float(len(RR) - non_rel_count))

    row = row +1 
    worksheet.write(row,col,"cosine-evaluation")
    worksheet.write(row,col+1,str(sum(AP)/(len(AP) - non_rel_count)))
    worksheet.write(row,col+2,str(sum(RR)/float(len(RR) - non_rel_count)))

    write_to_file('cosine-evaluation')

    AP = []
    RR = []
    p_at_5 = []
    p_at_20 = []
    PR_table_list = []
    non_rel_count = 0

    #stopped
    print 'stopped'
    count = 0    
    # for i in glob.glob("workbooks-stopped/*.xlsx"):
    #     i = i.rsplit(os.sep,1)[1]
    #     #print 'lol'
    #     count = count + 1
    #     #print(i)
    open_file('Output/stopped-bm25' + '.xlsx' ,relevance_dict,'stopped-bm25',"stopwords")

    

    print 'MAP : ' + str(sum(AP)/(len(AP) - non_rel_count))
    print 'MRR : ' + str(sum(RR)/float(len(RR) - non_rel_count))

    row = row +1 
    worksheet.write(row,col,"stopped-evaluation-bm25")
    worksheet.write(row,col+1,str(sum(AP)/(len(AP) - non_rel_count)))
    worksheet.write(row,col+2,str(sum(RR)/float(len(RR) - non_rel_count)))
    
    write_to_file('stopped-evaluation-25')


    AP = []
    RR = []
    p_at_5 = []
    p_at_20 = []
    PR_table_list = []
    non_rel_count = 0
    print 'lucene'
    count = 0  

    for i in glob.glob("Lucene/*.xls"):
        i = i.rsplit(os.sep, 1)[1]
        # print(i)
        open_file("Lucene/" + i, relevance_dict, 'LuceneCACM_Relevant', "lucene")

    print 'MAP : ' + str(sum(AP) / (len(AP) - non_rel_count))
    print 'MRR : ' + str(sum(RR) / (float(len(RR) - non_rel_count)))

    row = row +1 
    worksheet.write(row,col,"lucene-evaluation")
    worksheet.write(row,col+1,str(sum(AP)/(len(AP) - non_rel_count)))
    worksheet.write(row,col+2,str(sum(RR)/float(len(RR) - non_rel_count)))

    write_to_file('lucene-evaluation')

    # AP = []
    # RR = []
    # p_at_5 = []
    # p_at_20 = []
    # PR_table_list = []
    # non_rel_count = 0


    # print 'query-expansion-version2'
    # count = 0  

    # # query Expansion

    # # for i in glob.glob("workbooks-query-expansion-tf/*.xlsx"):
    # #     i = i.rsplit(os.sep,1)[1]
    # #     #print(i)
    # open_file("Output/query-expansion-versions2.xlsx",relevance_dict,'query-expansion-bm25','query_expansion_version2')

    # print 'query-expansion'
    # print 'MAP : ' + str(sum(AP) / (len(AP) - non_rel_count))
    # print 'MRR : ' + str(sum(RR) / float(len(RR) - non_rel_count))

    # row = row +1 
    # worksheet.write(row,col,"query-expansion-version2")
    # worksheet.write(row,col+1,str(sum(AP)/(len(AP)  - non_rel_count)))
    # worksheet.write(row,col+2,str(sum(RR)/float(len(RR) - non_rel_count)))

    # write_to_file("query-expansion-verison2")


    AP = []
    RR = []
    p_at_5 = []
    p_at_20 = []
    PR_table_list = []
    non_rel_count = 0

    # queri-expansion-version-1
    print 'query-expansion-version1'
    count = 0  

    open_file("Output/query-expansion-bm25-verison1.xlsx", relevance_dict, 'LuceneCACM_Relevant', "query-exp-version1")

    print 'lucene'
    print 'MAP : ' + str(sum(AP) / (len(AP) - non_rel_count))
    print 'MRR : ' + str(sum(RR) / (float(len(RR) - non_rel_count)))

    row = row +1 
    worksheet.write(row,col,"query-expansion-bm25-verison1")
    worksheet.write(row,col+1,str(sum(AP)/(len(AP) - non_rel_count)))
    worksheet.write(row,col+2,str(sum(RR)/float(len(RR) - non_rel_count)))

    write_to_file('query-exp-v1-evaluation')

    # AP = []
    # RR = []
    # p_at_5 = []
    # p_at_20 = []
    # PR_table_list = []
    # non_rel_count = 0

    # print 'query-expansion-version2'
    # count = 0  

    # open_file("Output/query-expansion-versions3.xlsx", relevance_dict, 'LuceneCACM_Relevant', "query-exp-version3")

    # print 'lucene'
    # print 'MAP : ' + str(sum(AP) / (len(AP) - non_rel_count))
    # print 'MRR : ' + str(sum(RR) / (float(len(RR) - non_rel_count)))

    # row = row +1 
    # worksheet.write(row,col,"query-expansion-versions3")
    # worksheet.write(row,col+1,str(sum(AP)/(len(AP) - non_rel_count)))
    # worksheet.write(row,col+2,str(sum(RR)/float(len(RR) - non_rel_count)))

    # write_to_file('query-expansion-verison3')

    # AP = []
    # RR = []
    # p_at_5 = []
    # p_at_20 = []
    # PR_table_list = []
    # non_rel_count = 0
    #     # for i in glob.glob("workbooks-query-expansion/*.xlsx"):
    #     #     i = i.rsplit(os.sep,1)[1]
    #         #print(i)
    # open_file("Output/stop-query-expansion-versions1.xlsx",relevance_dict,'query-expansion-bm25','query_expansion_cacm')

    # print 'query-expansion-stop-words'
    # print 'MAP : ' + str(sum(AP) / (len(AP) - non_rel_count))
    # print 'MRR : ' + str(sum(RR) / float(len(RR)  - non_rel_count))

    # row = row +1
    # worksheet.write(row,col,"query-expansion-stop-words")
    # worksheet.write(row,col+1,str(sum(AP)/(len(AP)  - non_rel_count)))
    # worksheet.write(row,col+2,str(sum(RR)/float(len(RR)  - non_rel_count)))

    # write_to_file('query-exp-stop-words-evaluation')

    AP = []
    RR = []
    p_at_5 = []
    p_at_20 = []
    PR_table_list = []
    non_rel_count = 0
        # for i in glob.glob("workbooks-query-expansion/*.xlsx"):
        #     i = i.rsplit(os.sep,1)[1]
            #print(i)
    open_file("Output/cosine_retrieval_stop_cacm.xlsx",relevance_dict,'query-expansion-bm25','query_expansion_cacm')

    print 'query-stemmed-bm25'
    print 'MAP : ' + str(sum(AP) / (len(AP) - non_rel_count))
    print 'MRR : ' + str(sum(RR) / float(len(RR)  - non_rel_count))

    row = row +1
    worksheet.write(row,col,"cosine_retrieval_stop_cacm")
    worksheet.write(row,col+1,str(sum(AP)/(len(AP)  - non_rel_count)))
    worksheet.write(row,col+2,str(sum(RR)/float(len(RR)  - non_rel_count)))

    write_to_file('cosine-stop-evaluation')

    # AP = []
    # RR = []
    # p_at_5 = []
    # p_at_20 = []
    # PR_table_list = []
    # non_rel_count = 0
    #     # for i in glob.glob("workbooks-query-expansion/*.xlsx"):
    #     #     i = i.rsplit(os.sep,1)[1]
    #         #print(i)
    # open_file("Output/query-expansion-bm25-verison1-run2.xlsx",relevance_dict,'query-expansion-bm25','query_expansion_cacm')

    # print 'query-stemmed-bm25'
    # print 'MAP : ' + str(sum(AP) / (len(AP) - non_rel_count))
    # print 'MRR : ' + str(sum(RR) / float(len(RR)  - non_rel_count))

    # row = row +1
    # worksheet.write(row,col,"query-expansion-verisons1-2-exp")
    # worksheet.write(row,col+1,str(sum(AP)/(len(AP)  - non_rel_count)))
    # worksheet.write(row,col+2,str(sum(RR)/float(len(RR)  - non_rel_count)))

    # #write_to_file('query-expansion-version1-query10')

    # AP = []
    # RR = []
    # p_at_5 = []
    # p_at_20 = []
    # PR_table_list = []
    # non_rel_count = 0
    #     # for i in glob.glob("workbooks-query-expansion/*.xlsx"):
    #     #     i = i.rsplit(os.sep,1)[1]
    #         #print(i)
    # open_file("Output/query-expansion-versions2-run2.xlsx",relevance_dict,'query-expansion-bm25','query_expansion_cacm')

    # print 'query-stemmed-bm25'
    # print 'MAP : ' + str(sum(AP) / (len(AP) - non_rel_count))
    # print 'MRR : ' + str(sum(RR) / float(len(RR)  - non_rel_count))

    # row = row +1
    # worksheet.write(row,col,"query-expansion-verisons2-2-qw")
    # worksheet.write(row,col+1,str(sum(AP)/(len(AP)  - non_rel_count)))
    # worksheet.write(row,col+2,str(sum(RR)/float(len(RR)  - non_rel_count)))

    workbook.close()
