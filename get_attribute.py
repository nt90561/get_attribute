# -*- coding: utf-8 -*-
import csv
import os

def _get_court(text):
    #法院別
    for line in text:
        line = line.decode('utf-8')
        if line[0:3] in (u"\"臺灣", u"\"台灣", u"\"福建"):
            return line[3:9].encode('utf-8')

def get_num_date_cu(text):
    #字號 日期 法院別
    text.seek(0, 0)
    f_csv = csv.reader(text)
    NDC = []
    for line in f_csv:
        if line[0].decode('utf-8') == u"【裁判案由】":
            break
        NDC.append(line[1])
    NDC.append(_get_court(text))
    #回傳list
    return NDC

def get_law(text):
    text.seek(0, 0)
    for line in text:
        line = line.decode('utf-8')
        if line[0:4] in (u"上列被告", u"以上被告", u"上列上訴", u"上列自訴"):
            law_name = line[line.find(u"因")+1:line.find(u"案件")]
            #回傳str
            return law_name.encode('utf-8')

def get_accused(text, tag=1):
    text.seek(0, 0)
    accused = []
    state = 0
    for line in text:
        line = line.decode('utf-8')
        if line[0:4] in (u"上列被告", u"以上被告", u"上列上訴", u"上列自訴"):
            break
        if state == 1:
            char = line.strip("\r\n").replace(" ", "").replace(u"　", "")
            if not char.find(u"辯護人")+1 and not char.find(u"律師")+1 and not char.find(u"輔佐人")+1:
                if line[6:] and line[:10] != u"　　　　　　　　　　":
                    ch = line[6:].strip("\r\n")
                    if ch[3:].find(u"　") + 1:
                        ch = ch[:ch.find(u"　")]
                    if char.find(u"代表人") + 1:
                        ch += u"（代表人）"
                    if char.find(u"法定代理人") +1:
                        ch += u"（代表人）"
                    elif char.find(u"代理人") + 1:
                        ch += u"（代理人）"
                    if ch.strip():
                        accused.append(ch.strip(u".").encode('utf-8'))
        if line[0:5] in (u"公　訴　人", u"聲　請　人", u"上　訴　人", u"自　訴　人"):
            state = 1
    if tag == 1:
        return accused
    elif tag == 2:
        return len(accused)

file_list = []
for (a, b, c) in os.walk('output/'):
    file_list.extend(c)
file_list = tuple(file_list)

out = open("output.csv", "wb")
out_csv = csv.writer(out)

data_row = []

for filename in file_list:
    textfile = os.path.join('output/', filename)
    data_row.append(filename)
    with open(textfile, "r") as f:
        data_row.extend(get_num_date_cu(f))
        s =";".join(get_accused(f))
        data_row.append(get_law(f))
        data_row.append(get_accused(f, 2))
        data_row.append(s)

    out_csv.writerow(data_row)
    data_row = []

out.close()

