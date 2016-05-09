import pandas as pd
import random
import os

directory = os.path.dirname(os.path.realpath(__file__))
read_file = os.path.join(directory, "data\checkbook2015.csv")

# number of records in file (excludes header)
n = sum(1 for line in open(read_file)) - 1

#desired sample size
s = 20000

# Creates a 
skip = sorted(random.sample(xrange(1, n+1), n-s))
df = pd.read_csv(read_file, skiprows=skip)

write_file = os.path.join(directory, "data\checkbook2015Sample.csv")
df.to_csv(write_file)


#cb = pd.read_csv(read_file, nrows=200)