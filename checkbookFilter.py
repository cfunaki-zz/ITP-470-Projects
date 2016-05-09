import os
import csv

directory = os.path.dirname(os.path.realpath(__file__))
read_file = os.path.join(directory, "data\eCheckbook_Data.csv")
write_file = os.path.join(directory, "data\checkbook2015.csv")

rfile = open(read_file, 'r')
reader = csv.reader(rfile)
#data = list(reader)
#file.close()
wfile = open(write_file, 'wb')
writer = csv.writer(wfile)

for i, row in enumerate(reader):
    if row[1] == '2015' or i == 0:
        writer.writerows([row])
        
rfile.close()
wfile.close()
