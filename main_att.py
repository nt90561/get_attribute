#!/usr/bin/env python2.7
# -*- coding:utf-8 -*-
import csv
import os
import re

from get_attribute import get_accused
from convert_digit import uppercase_to_digits, uppertime_to_day

area = (u"臺北市", u"新北市", u"臺北縣", u"桃園市", u"桃園縣", u"臺中市", u"臺南市", u"高雄市",
        u"基隆市", u"新竹市", u"嘉義市", u"新竹縣", u"苗栗縣", u"彰化縣", u"南投縣", u"雲林縣",
        u"嘉義縣", u"屏東縣", u"宜蘭縣", u"花蓮縣", u"臺東縣", u"澎湖縣", u"金門縣", u"連江縣")

def clear_name(name):

    name2 = name.replace(u"（代表人）", "").replace(u"（代理人）", "").replace(u"（已解散）", "")
    if name2.find(u"（原名") + 1 or name2.find(u"（即") + 1 or name2.find(u"（已") + 1:
        name2 = name2[:name2.find(u"（")]
    if name2.find(u"原名") + 1:
        name2 = name2[:name2.find(u"原名")]
    if name2.find(u"冒名") + 1:
        name2 = name2[:name2.find(u"冒名")]

    return name2


def get_sentence(text):
    if type(text) != unicode:
        text = text.decode("utf-8")
    text = text.replace(u"。", u"，").replace(u"；", u"，")
    lines = text.split(u"，")
    prison = "-"
    probation = "-"
    fine = "-"
    change = "-"
    bribe = "-"
    bribe_li = []
    sheet = ""
    for line in lines:
        if re.search(u"(繳回之|犯罪|回扣)?所得\S+元", line):
            bribe = re.search(u"(繳回之|犯罪|回扣)?所得\S+元", line).group()
            bribe = line[line.find(u"所得")+2:line.find(u"元")]
            bribe = uppercase_to_digits(re.sub(u"(財物|賄賂|不正利益|共計?|新[臺台]幣)", "", bribe))
            bribe_li.append(bribe)

        if line.find(u"免刑") + 1:
            sheet = u"免刑"
        else:
            if line.find(u"無期徒刑") + 1:
                prison = u"無期徒刑"
                change = "F"
            elif line.find(u"有期徒刑") + 1:
                prison = line[line.find(u"有期徒刑") + 4:]
                prison = uppertime_to_day(prison)
                change = "F"
            elif line.find(u"拘役") + 1:
                prison = line[line.find(u"拘役") + 2:]
                prison = uppertime_to_day(prison)
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
                fine = fine.strip(u"新台幣").strip(u"新臺幣")
                fine = uppercase_to_digits(fine)
    prison = prison.encode("utf-8")
    fine = fine.encode("utf-8")
    probation = probation.encode("utf-8")
    bribe = "/".join(bribe_li).encode("utf-8")
    if (prison, change, fine, probation) == ("-", "-", "-", "-"):
        if sheet:
            sheet = sheet.encode("utf-8")
            return [sheet]
        else:
            return ["needcheck"]
    else:
        return [bribe, prison, change, fine, probation]


def crime_justify(crime):
    crime_f = ""

    #貪污治罪條例
    if crime.find(u"不違背職務收受賄賂")+1\
            or re.search(u"對於職務上之?行為，?((收受)|(要求))((賄賂)|(不正利益))", crime)\
            or crime.find(u"之職務上行為收受賄賂")+1 or crime.find(u"不違背職務要求賄賂")+1\
            or crime.find(u"第五條第一項第三款")+1:
        crime_f = u"不違背職務受賄罪"
    elif re.search(u"違背職務((收受)|(要求)|(期約))賄賂", crime)\
            or re.search(u"[對關]於違背職務之行為，?((收受)|(要求)|(期約))", crime)\
            or crime.find(u"違背職務收受不正利益")+1\
            or re.search(u"悖職((收受)|(期約))賄賂", crime)\
            or crime.find(u"第四條第一項第五款")+1:
        crime_f = u"違背職務受賄罪"
    if re.search(u"貪污治罪條例第((十一)|(11))條", crime)\
            or re.search(u"關於不?違背職務之行為，?((交付)|(行求))", crime)\
            or crime.find(u"不違背職務交付賄賂")+1 or crime.find(u"違背職務行求、期約賄賂")+1\
            or crime.find(u"違背職務行賄罪")+1\
            or re.match(u"非公務員\S+職務上期約賄賂", crime):
        crime_f = u"行賄罪"
    if re.search(u"((利用)|(假借))職務上之?機會，?\S*詐(欺)?取財(物)?", crime)\
            or crime.find(u"職務機會詐取財物")+1\
            or re.search(u"職務上之?機會，以詐術使人", crime):
        crime_f = u"利用職務詐取財物罪"
    if re.search(u"((主管)|(監督))之?事[物務](直接)?圖利", crime) or crime.find(u"第六條第一項第四款")+1\
            or re.search(u"((主管)|(監督))之事務，明知違背\S*法[令律]\S*([直間]接)?圖\S*利益", crime):
        crime_f = u"圖利罪"
    if re.search(u"((侵占)|(竊取))公[有用]((財物)|(器材))", crime)\
            or crime.find(u"侵占職務上")+1\
            or re.search(u"公務員\S*竊取", crime):
        if not crime.find(u"因公務員竊取公有財物罪所得之財物")+1:
            crime_f = u"侵占/竊取公有財物罪"
    if re.search(u"[購經]辦公用((器材)|(工程))", crime):
        crime_f = u"公用工程收取回扣罪"
    if re.search(u"(藉勢)?\S?(藉端)?((勒索)|(強占))財物", crime):
        crime_f = u"藉勢藉端勒索財物罪"
    if re.search(u"收受貪污所得財物", crime) or crime.find(u"竊取公有財物罪所得之財物，故為故買")+1:
        crime_f = u"收受貪污所得財物罪"

    #普通刑法
    if crime.find(u"供前具結，而為虛偽陳述")+1:
        crime_f = u"偽證罪"
    if re.search(u"洩漏(關於)?(中華民國)?國防以外", crime):
        crime_f = u"一般洩密罪"
    if crime.find(u"意圖為自己不法之所有，以詐術使人將")+1 or crime.find(u"詐欺得利罪")+1\
            or crime.find(u"詐欺取財")+1:
        if not crime_f:
            crime_f = u"詐欺罪"
    if crime.find(u"恐嚇取財")+1 or crime.find(u"恐嚇得利")+1:
        crime_f = u"恐嚇得利罪"
    if crime.find(u"侵占")+1:
        if not crime_f:
            crime_f = u"侵占罪"
    if re.search(u"((從事業務之人，)|(公務員))明知為不實之?事項", crime)\
            or re.search(u"(行使)?((業務上?)|(公務員))登載不實(文書)?", crime)\
            or re.search(u"[偽變]造((特種)|(私))文書", crime)\
            or crime.find(u"公文書登載不實")+1:
        crime_f = u"偽造文書罪"
    if crime.find(u"賭博")+1:
        crime_f = u"賭博罪"
    if crime.find(u"竊盜")+1:
        crime_f = u"竊盜罪"
    if crime.find(u"背信")+1:
        crime_f = u"背信罪"
    if re.search(u"女子與他人為((猥褻)|(性交))之行為", crime)\
            or re.search(u"(圖利)?容留((猥褻)|(性交))", crime):
        crime_f = u"圖利容留性交罪"

    #其他
    if re.search(u"政府採購法", crime) or crime.find(u"意圖影響決標價格")+1\
            or crime.find(u"意圖影響採購結果")+1 or crime.find(u"使開標發生不正確")+1\
            or re.search(u"受機關委託提供\S*人員，意圖為\S+違反法令之(限制)?\S?(審查)?，因而獲得利益", crime):
        crime_f = u"政府採購法"
    if re.search(u"商業會計法第((71)|(七十一))條", crime)\
            or re.search(u"以明知為不實之事項，而填[製載]會計憑證", crime)\
            or crime.find(u"商業負責人利用不正當方法，致使財務報表")+1:
        crime_f = u"填製會計憑證不實罪"
    if crime.find(u"洗錢防制法")+1 or crime.find(u"因重大犯罪所得財物之洗錢行為")+1:
        crime_f = u"洗錢罪"
    if crime.find(u"非法清理廢棄物")+1 or crime.find(u"從事廢棄物清除")+1:
        crime_f = u"非法清理廢棄物罪"
    if crime.find(u"大陸地區人民非法進入臺灣地區")+1:
        crime_f = u"大陸地區人民非法進入臺灣地區罪"
    if crime.find(u"非法輸入檢疫物罪")+1:
        crime_f = u"非法輸入檢疫物罪"
    if crime.find(u"農會法")+1:
        crime_f = u"農會法"
    if crime.find(u"電磁紀錄罪")+1:
        crime_f = u"電磁紀錄罪"
    if crime.find(u"山坡地保育利用條例")+1:
        crime_f = u"山坡地保育利用條例"
    if crime.find(u"毒品")+1:
        crime_f = u"毒品危害防制條例"
    if crime.find(u"未經當事人之同意，非公務機關對個人資料為蒐集及電腦處理")+1:
        crime_f = u"個資法"
    if crime.find(u"電子遊戲場業管理條例第22條")+1:
        crime_f = u"電子遊戲場業管理條例"

    if not crime_f:
        return crime
    else:
        return crime_f




file_list = []
for (a, b, c) in os.walk('output/'):
    file_list(c)
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

        for line in f:  # 抓取主文
            line = line.strip("\n").replace(" ", "").decode('utf-8')
            line = line.replace(u"　", "")
            if line in (u"事實", u"事實及理由", u"理由", u"犯罪事實及理由", u"犯罪事實"):
                break
            if state == 1:
                maintext.append(line)

            if line == u"主文":
                state = 1
        jud_crime = ""
        for line in maintext:  # 判決書非定罪判決的狀況
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

        for name_o in accused:
            #被告依序抓取判決結果--包含宣告罪與宣告刑
            name_o = name_o.decode("utf-8")
            name = clear_name(name_o)
            crime = ""
            bribe = ""
            job = ""
            sentence = []
            covered = 0
            for line in maintext:
                if line.find(name) + 1:

                    cc = sorted([line.find(u"，處"), line.find(u"，各處"), line.find(u"，所處"),
                                 line.find(u"，分別處"), line.find(u"，量處"), line.find(u"，各量處"),
                                 line.find(u"，科"), line.find(u"，各科"), line.find(u"應執行"),
                                 line.find(u"，免刑"), line.find(u"，免除其刑"), line.find(u"，均免刑"),
                                 line.find(u"，均免除其刑")])
                    e = max(cc)
                    if e + 1:  # 有罪的處理

                        n = 0
                        e = cc[n]
                        while e == -1:
                            e = cc[n]
                            n += 1

                        s = line.find(name) + len(name)
                        if s < e:  # 抓取宣告刑
                            sen = re.compile(u"應執行\S+[；。]")
                            pp = sen.search(line)
                            if line.find(u"應執行") + 1:
                                sentence = get_sentence(pp.group())
                            elif line.find(u"減為") + 1:
                                sentence = get_sentence(line[line.find(u"減為"):])
                            else:
                                sentence = get_sentence(line[e + 1:])

                            crime = line[s:e].lstrip(u"】")
                            for one in accused:
                                one = one.decode("utf-8")
                                crime = crime_justify(crime)
                            break


                    elif line.find(u"免刑") + 1 or line.find(u"免除其刑") + 1:
                        crime = line[line.find(name) + len(name):line.find(u"，")]
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
            if crime.find(u"如附表") + 1:
            #遇到附表的處理
                pass

            if not crime:
            #沒抓到宣告罪的處理
                if jud_crime:
                    crime = jud_crime
                elif covered:
                    crime = "covered"
                else:
                    crime = "need check"
                    attlog_csv.writerow([filename, name.encode("utf-8")])

            state2 = 0
            for line in f:  # 抓取被告工作職位
                line = line.strip("\n").replace(" ", "").decode('utf-8')
                line = line.replace(u"　", "")
                if state2 == 2:  # 從判決書的事實段落往下抓
                    line = re.sub(u"\(\S+?\)", "", line)
                    line = re.sub(u"（\S+?）", "", line)

                    p1_str = u"(" + name + u")" + u"\S*?[為係任乃]\S*?" +\
                             u"(受刑人|清算人|承辦人|經紀人|所有權人|員|長|代表|主席|主任|助理|負責人|(員工)|(員警)|" +\
                             u"經理|業者|會計|[一乙]職|職務|秘書|幹事|官|司|師|技術?[士工佐正]|(工友)" +\
                             u"|司機|偵察佐|巡佐|船主|替代役|法警)" +\
                             u"(後|迄今)?[、；，。]"

                    pattern1 = re.compile(p1_str)
                    job_1 = pattern1.search(line)

                    if job_1:
                        job = job_1.group()[:-1]
                        if len(job) > 100:
                            pass
                        else:

                            f.seek(0, 0)
                            break
                if line in (u"事實", u"事實及理由", u"理由", u"犯罪事實及理由", u"犯罪事實"):
                    state2 = 2
            else:
                job = "to_check"
                f.seek(0, 0)




            name_o = name_o.encode("utf-8")
            crime = crime.encode("utf-8")
            job = job.encode("utf-8")

            accu_att = [name_o, job, crime]
            accu_att.extend(sentence)
            attr_csv.writerow(accu_att)


    out_csv.writerow(data_row)
    data_row = []

out.close()
attlog.close()