# -*- coding:utf-8 -*-
import csv
import os
import re

from get_attribute import get_accused


def clear_name(name_li):
    c_names = []
    for name in name_li:
        name = name.decode("utf-8")
        name2 = name.replace(u"（代表人）", "").replace(u"（代理人）", "").replace(u"（已解散）", "")
        if name2.find(u"（原名") + 1 or name2.find(u"（即") + 1 or name2.find(u"（已") + 1:
            name2 = name2[:name2.find(u"（")]
        if name2.find(u"原名") + 1:
            name2 = name2[:name2.find(u"原名")]
        if name2.find(u"冒名") + 1:
            name2 = name2[:name2.find(u"冒名")]
        c_names.append(name2.encode("utf-8"))
    return c_names


def get_sentence(text):
    if type(text) != unicode:
        text = text.decode("utf-8")
    text = text.replace(u"。", u"，").replace(u"；", u"，")
    lines = text.split(u"，")
    prison = "-"
    probation = "-"
    fine = "-"
    change = "-"
    sheet = ""
    for line in lines:
        if line.find(u"免刑") + 1:
            sheet = u"免刑"
        else:
            if line.find(u"無期徒刑") + 1:
                prison = u"無期徒刑"
                change = "F"
            elif line.find(u"有期徒刑") + 1:
                prison = line[line.find(u"有期徒刑") + 4:]
                change = "F"
            elif line.find(u"拘役") + 1:
                prison = line[line.find(u"拘役") + 2:]
                change = "F"
            elif re.search(u"如\S+所示之\S*刑", line):
                sheet = line[line.find(u"如"):]
            elif re.search(u"科\S+所示之罰金", line):
                sheet = line[line.find(u"科"):]
            if re.search(u"緩刑\S+年", line):
                probation = line[line.find(u"緩刑") + 2:]
            if line.find(u"易科罰金") + 1:
                change = "T"
            elif re.search(u"罰金\S+元", line):
                fine = line[line.find(u"罰金") + 2:]
    prison = prison.encode("utf-8")
    fine = fine.encode("utf-8")
    probation = probation.encode("utf-8")
    if (prison, change, fine, probation) == ("-", "-", "-", "-"):
        if sheet:
            sheet = sheet.encode("utf-8")
            return [sheet]
        else:
            return ["needcheck"]
    else:
        return [prison, change, fine, probation]


file_list = []
for (a, b, c) in os.walk('output/'):
    file_list.extend(c)
file_list = tuple(file_list)

out = open("output.csv", "wb")
out_csv = csv.writer(out)

attlog = open("log.csv", "wb")
attlog_csv = csv.writer(attlog)
data_row = []

for filename in file_list:
    textfile = os.path.join('output/', filename)
    attr_file = os.path.join('attru/', filename)
    file = open(attr_file, 'w+')
    file.close()

    data_row.append(filename)
    with open(textfile, "r") as f:
        state = 0
        maintext = []
        for line in f:
            line = line.strip("\n").replace(" ", "").decode('utf-8')
            line = line.replace(u"　", "")
            if line in (u"事實", u"事實及理由", u"理由", u"犯罪事實及理由", u"犯罪事實"):
                break
            if state == 1:
                maintext.append(line)
            if line == u"主文":
                state = 1
        jud_crime = ""
        for line in maintext:
            if line.find(u"上訴駁回") + 1:
                jud_crime = u"上訴駁回"
            if line[0:2] == u"本件":
                if line.find(u"不受理") + 1:
                    jud_crime = u"不受理"
                elif line.find(u"免訴") + 1:
                    jud_crime = u"免訴"
                elif line.find(u"管轄錯誤") + 1:
                    jud_crime = u"管轄錯誤"
                else:
                    jud_crime = line
                data_row.append(jud_crime.encode("utf-8"))

        accused = get_accused(f)
        attr = open(attr_file, "wb")
        attr_csv = csv.writer(attr)

        for name in accused:
            name = name.decode("utf-8")
            crime = ""
            sentence = []
            covered = 0
            for line in maintext:

                name2 = name.replace(u"（代表人）", "").replace(u"（代理人）", "") \
                    .replace(u"（已解散）", "")
                if name2.find(u"（原名") + 1 or name2.find(u"（即") + 1 or name2.find(u"（已") + 1:
                    name2 = name2[:name2.find(u"（")]
                if name2.find(u"原名") + 1:
                    name2 = name2[:name2.find(u"原名")]
                if name2.find(u"冒名") + 1:
                    name2 = name2[:name2.find(u"冒名")]

                if line.find(name2) + 1:

                    cc = sorted([line.find(u"，處"), line.find(u"，各處"), line.find(u"，所處"),
                                 line.find(u"，分別處"), line.find(u"，量處"), line.find(u"，各量處"),
                                 line.find(u"，科"), line.find(u"，各科"), line.find(u"應執行"),
                                 line.find(u"，免刑"), line.find(u"，免除其刑")])
                    e = max(cc)
                    if e + 1:

                        n = 0
                        e = cc[n]
                        while e == -1:
                            e = cc[n]
                            n += 1

                        s = line.find(name2) + len(name2)
                        if s < e:
                            sen = re.compile(u"應執行\S+[；。]")
                            pp = sen.search(line)
                            if line.find(u"應執行") + 1:
                                sentence = get_sentence(pp.group())
                            elif line.find(u"減為") + 1:
                                sentence = get_sentence(line[line.find(u"減為"):])
                            else:
                                sentence = get_sentence(line[e + 1:])

                            crime = line[s:e].replace(u"、", "").lstrip(u"】")
                            for one in clear_name(accused):
                                one = one.decode("utf-8")
                                crime = crime.replace(one, "")
                            break
                    elif line.find(u"免刑") + 1 or line.find(u"免除其刑") + 1:
                        crime = line[line.find(name2) + len(name2):line.find(u"，")]
                        if not crime:
                            crime = u"免刑"
                    elif line.find(u"無罪") + 1:
                        crime = u"無罪"
                    elif line.find(u"免訴") + 1:
                        crime = u"免訴"
                    elif line.find(u"不受理") + 1:
                        crime = u"不受理"
                    elif line.find(u"管轄錯誤") + 1:
                        crime = u"管轄錯誤"
                elif line.find(u"○○") + 1:
                    covered = 1

            if not crime:
                if jud_crime:
                    crime = jud_crime
                elif covered:
                    crime = "covered"
                else:
                    crime = "need check"
                    attlog_csv.writerow([filename, name.encode("utf-8")])

            name = name.encode("utf-8")
            crime = crime.encode("utf-8")
            accu_att = [name, crime]
            accu_att.extend(sentence)
            attr_csv.writerow(accu_att)

    out_csv.writerow(data_row)
    data_row = []

out.close()
attlog.close()