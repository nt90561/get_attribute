# -*- coding: utf-8 -*-

import os
import csv

file_list = []
for (a, b, c) in os.walk('attru/'):
    file_list.extend(c)
file_list = tuple(file_list)

out = open("total_att.csv", "wb")
out_csv = csv.writer(out)

data_row = []

for filename in file_list:
    textfile = os.path.join('attru/', filename)
    with open(textfile, "r") as f:
        f_csv = csv.reader(f)
        for row in f_csv:
            row.insert(0, filename)
            out_csv.writerow(row)

out.close()