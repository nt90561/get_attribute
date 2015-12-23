# -*- coding:utf-8 -*-

import csv
import re

from main_att import crime_justify

alt = open("total_att_alt.txt", "w+")

crime_li = []

with open("total_att.csv", "rb") as f:
    f_csv = csv.reader(f)
    for row in f_csv:
        crime = row[2].decode("utf-8")
        crime = crime_justify(crime)
        if not re.search(u"附表\S*所[示載]\S*之?\S*罪", crime):
            crime = crime.encode("utf-8")
            if crime not in crime_li:
                crime_li.append(crime)
                alt.write(crime + "\n")

alt.close()
