import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from dateutil.parser import parse

# Set your directory and the file you want to open
directory = os.path.dirname(os.path.realpath(__file__))
read_file = os.path.join(directory, "data\checkbook2015Sample.csv")

# Open file from csv into a DataFrame
cb = pd.read_csv(read_file)

# Set variable for the "CALENDAR MONTH" variable in the dataframe
# This simply makes it easier to access
cbMonths = cb['CALENDAR MONTH']

# List of the calendar months in order, allows us to sort out bar chart
month_list = ['JANUARY','FEBRUARY','MARCH','APRIL','MAY',
          'JUNE','JULY','AUGUST','SEPTEMBER','OCTOBER',
          'NOVEMBER','DECEMBER']

# Count how many transactions are in each month
cbMonthCount = cbMonths.value_counts().reindex(month_list)
# Plot this on a bar chart. Which month has the most transactions?
cbMonthCount.plot(kind='bar')

# Let's get the dollar amounts in the "DOLLAR AMOUNT" variable
# It is stored as a string, so we will need to convert it to a numeric data type
cb['DOLLAR AMOUNT'] = cb['DOLLAR AMOUNT'].str.replace("$", "").astype(float)

# What are the highest and lowest transaction amounts?
# The total of all transactions?
print "Max: ", max(cb['DOLLAR AMOUNT'])
print "Min: ", min(cb['DOLLAR AMOUNT'])
print "Sum: ", sum(cb['DOLLAR AMOUNT'])

# Lambda functions allow you to apply a function to every row of the DataFrame
# This function converts the variable to a datetime data type
cb['TRANSACTION DATE'] = cb.apply(lambda t: parse(t['TRANSACTION DATE']), axis=1)

# You can get the day of the week from datetime variables
# Here we create another variable for the day of the week
cb['DAY OF WEEK'] = cb.apply(lambda t: t['TRANSACTION DATE'].dayofweek, axis=1)

cbDay = cb['DAY OF WEEK']

# Let's count how many transactions occurred on each day of the week
cbDayCount = cbDay.value_counts().reindex(range(0, 5, 1))
# And again we can plot this in a bar chart
cbDayCount.plot(kind='bar')

# Now let's look at the departments in our dataset
cbDep = cb['DEPARTMENT NAME']
# This gets a unique list of the departments
departments = list(cbDep.unique())

# We can subset one department
police = cb[cbDep == 'POLICE']

# We can also find the sum of the transactions, grouped by department
depSum = cb.groupby('DEPARTMENT NAME')['DOLLAR AMOUNT'].sum()
dfDepSum = pd.DataFrame(depSum)

# Here we are finding the number of transactions, grouped by department
depCount = cb.groupby('DEPARTMENT NAME')['DOLLAR AMOUNT'].count()
dfDepCount = pd.DataFrame(depCount)

# Let's look for Sharpies
# This method allows us to find all transactions that involved sharpies
mask = np.array(['SHARPIE' in x for x in cb['DESCRIPTION']])
cbSharpie = cb[mask]
# And then we can see the total spending on Sharpies
print "Sharpie spending: ", sum(cbSharpie['DOLLAR AMOUNT'])


