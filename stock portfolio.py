import pandas as pd
import numpy as np
import os
from dateutil.parser import parse
import matplotlib.pyplot as plt

directory = 'C:/Users/Chris/Documents/Stocks/Portfolio'

buy_threshold = 0.009
rtn_target = 0.005
buy_interval = 1
sell_interval = 3
short_window = 3
long_window = 10

start_amt = 100000.0
bank = start_amt
bank_amt = []
rolling_window = 39*20
multiplier = start_amt / 100000.0
    
companies = []
buys = []
shares = []
sales = []
counter = []
i = 0
n = 4

first = True
stock_files = os.listdir(directory)

for stock_file in stock_files[3:4]:
    stock = pd.read_excel('%s/%s' % (directory, stock_file))
    
    # Get date into proper datetime format
    try:
        stock.Date = stock.apply(lambda time: parse(time.Date), axis=1)
    except:
        pass
    stock.index = stock.Date
    stock = stock.between_time(start_time = '09:30:00', end_time = '16:00:00', include_end = False)
    
    # High price at 10 minute intervals
    stock_high = pd.DataFrame(stock.HIGH.resample('10Min', how='max'))
    stock_high['TIME'] = stock_high.index
    
    # Low price at 10 minute intervals
    stock_low = pd.DataFrame(stock.LOW.resample('10Min', how='min'))
    stock_low['TIME'] = stock_low.index
    
    # Signal - 20 d rolling average
    stock['SIGNAL'] = pd.rolling_mean(stock.OPEN, window=rolling_window)
    stock_signal = pd.DataFrame(stock.SIGNAL.resample('10Min', how='mean'))
    stock_signal['TIME'] = stock_signal.index
    
    # Short run exponential moving average
    stock['SHORT'] = pd.ewma(stock.OPEN, span=short_window)
    stock_short = pd.DataFrame(stock.SHORT.resample('10Min', how='min'))
    stock_short['TIME'] = stock_short.index
    
    # Long run exponential moving average
    stock['LONG'] = pd.ewma(stock.OPEN, span=long_window)
    stock_long = pd.DataFrame(stock.LONG.resample('10Min', how='min'))
    stock_long['TIME'] = stock_long.index
    
    # Previous close variable
    day_close = pd.DataFrame(stock.OPEN.resample('B', how='last'))
    day_close['PREV'] = day_close.OPEN.shift(1)
    del day_close['OPEN']
    day_close['day'] = day_close.index.dayofyear
    stock['day'] = stock.index.dayofyear
    stock = pd.merge(stock, day_close, how='left', on='day')
    stock.index = stock.Date
    stock_prev = pd.DataFrame(stock.PREV.resample('10Min', how='first'))
    stock_prev['TIME'] = stock_prev.index
    
    # Merge high, low, and previous close difference
    stock_merged = pd.merge(stock_high, stock_low, on='TIME', how='left')
    stock_merged = pd.merge(stock_merged, stock_prev, on='TIME', how='left')
    stock_merged = pd.merge(stock_merged, stock_signal, on='TIME', how='left')
    stock_merged = pd.merge(stock_merged, stock_short, on='TIME', how='left')
    stock_merged = pd.merge(stock_merged, stock_long, on='TIME', how='left')
    stock_merged = stock_merged[np.isnan(stock_merged.HIGH) == False]
    
    company = stock_file[:len(stock_file) - 5]
    #print company, len(stock_merged.index)
    companies.append(company)
    
    stock_merged['%s_HIGH'%company] = stock_merged.HIGH
    del stock_merged['HIGH']
    stock_merged['%s_LOW'%company] = stock_merged.LOW
    del stock_merged['LOW']
    stock_merged['%s_PREV'%company] = stock_merged.PREV
    del stock_merged['PREV']
    stock_merged['%s_SIGNAL'%company] = stock_merged.SIGNAL
    del stock_merged['SIGNAL']
    stock_merged['%s_SHORT'%company] = stock_merged.SHORT
    del stock_merged['SHORT']
    stock_merged['%s_LONG'%company] = stock_merged.LONG
    del stock_merged['LONG']
    
    stock_merged = stock_merged[rolling_window:]    
    
    if first == True:
        stocks = stock_merged
        first = False
    else:
        stocks = pd.merge(stocks, stock_merged, on='TIME', how='outer')
    shares.append([])
    counter.append(0)

stocks = stocks[:-11]
stocks.index = stocks.TIME
del stocks['TIME']

try:    
    stocks.index = stocks.apply(lambda time: parse(time.index), axis=1)
except:
    pass

for index, time in stocks.iterrows():
    
    i = 0
    for company in companies:        
        
        low_price = time['%s_LOW'%company]
        high_price = time['%s_LOW'%company]
        signal = time['%s_SIGNAL'%company]
        prev_close = time['%s_PREV'%company]
        short_ma = time['%s_SHORT'%company]
        long_ma = time['%s_LONG'%company]
        if len(shares[i]) == 0: # If no shares owned
            if (((low_price - prev_close) / prev_close) < -buy_threshold) \
            :#and short_ma < long_ma:
            
                if bank - low_price >= 0: # Is there money in the bank
                    quantity = int(1 * multiplier)
                    bank -= (quantity * low_price)
                    buys.append([index.dayofyear,company, quantity, low_price, bank])
                    for n in range(quantity):
                        shares[i].append(low_price)
                      
        else: # If shares owned
            counter[i] = counter[i] + 1
            avg_price = sum(shares[i]) / len(shares[i])
            rtn = (high_price - avg_price) / avg_price
            
            if rtn < rtn_target \
            and counter[i] % buy_interval == 0 \
            : #and short_ma < long_ma:
                #quantity = int( ((signal - low_price) / signal * 8) ** 2 )
                quantity = int(1 * multiplier)
                purchase_price = quantity * low_price
                if bank - purchase_price >= 0 and quantity > 0:
                    bank -= purchase_price
                    buys.append([index.dayofyear,company, quantity, low_price, bank])
                    for n in range(quantity):
                        shares[i].append(low_price)
            elif rtn >= rtn_target \
            and counter[i] % sell_interval == 0 \
            and short_ma <= long_ma * 1.00:
                quantity = len(shares[i])
                sale = high_price * quantity
                profit = rtn * quantity * avg_price
                bank += sale
                sales.append([index.dayofyear, company, quantity, high_price, avg_price, rtn*100, profit])
                shares[i] = []
                counter[i] = 0

        i += 1
    bank_amt.append(bank)
    i = 0

buys = pd.DataFrame(buys, columns=['day','company','quantity','price', 'bank'])
sales = pd.DataFrame(sales, columns=['day','company','quantity','price','avg price','return','profit'])

results = []
# Sell all remaining shares to get final bank amount
for company in companies:
    invested = sum(buys[buys.company==company].quantity * buys[buys.company==company].price)
    final_sale = stocks['%s_HIGH'%company][-1] * len(shares[i])
    bank = bank + final_sale
    sold = sum(sales[sales.company==company].quantity * sales[sales.company==company].price) + final_sale
    rtn = (sold - invested) / invested * 100
    #print company, rtn, '%'
    results.append([company, invested, sold, sold-invested,rtn])
    i = i + 1

results = pd.DataFrame(results, columns=['company','invested','sold','profit','return'])

#bank_amt.append(bank)

bank_amt = pd.Series(bank_amt)
bank_amt.index = stocks.index
bank_amt.plot()

print results.head()


total_rtn = (bank - start_amt) / start_amt * 100.0
invested_rtn = (sum(results.sold) - sum(results.invested)) / sum(results.invested) * 100.0
annual_rtn = ((bank / start_amt) ** (365 / (stocks.index.dayofyear[-1] - stocks.index.dayofyear[0])) - 1) * 100

print ''
print 'Bank Balance: ', '$', bank
print 'Total Return: ', total_rtn, '%'
print 'Total Invested: ', '$', sum(results.invested)
print 'Invested Return: ', invested_rtn, '%'
print 'Annual Return: ', annual_rtn, '%'
