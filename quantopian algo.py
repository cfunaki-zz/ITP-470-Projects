
import numpy as np
import math
import datetime as dt

def initialize(context):
    # Stocks used are Disney, Apple, and S&P500
    context.stocks = symbols('DIS', 'AAPL', 'SPY')
    
    context.interval = 15 # Interval in terms of minutes
    context.minute = 0
    

def handle_data(context, data):
    
    # This makes it so the algo only runs for every 15 minute interval
    context.minute += 1
    if (context.minute % context.interval == 0):
        
        V = history(60, '1m', 'volume') # Trading volume over the last 60 minutes
        P = history(60 + context.interval, '1m', 'price') # Price over last 60 minutes
        LP = history(180, '1m', 'price')
        #CP = history(2, '1d', 'close_price') # Closing price of the previous day
        hour = get_datetime('US/Eastern').hour
    
        # For each stock in the portfolio...
        for stock in context.stocks:
            #print(stock.symbol, CP[stock][0]) # Previous day closing price
            
            #print('Price', data[stock].price) # Current price
            #print('Now', P[stock][len(P)-1]) # Current price
            #print('Hour ago', P[stock][0]) # Price one hour ago
            # time = dt.datetime.now()
            
            # only run near market open/close
            if(hour <11 or hour > 14):
                # Get the price % change for the current 15 minute interval
                priceCurrent = data[stock].price
                priceHourAgo = P[stock][context.interval]
                pctChange = (priceCurrent - priceHourAgo) / priceHourAgo * 100
            
                # Get the price % change for the previous 15 minute interval
                priceCurrent2 = P[stock][len(P)-context.interval-1]
                priceHourAgo2 = P[stock][0]
                pctChange2 = (priceCurrent2 - priceHourAgo2) / priceHourAgo2 * 100
            
                # Get the average volume for the last 15 minutes, compared to the last hour
                volumeCurrent = V[stock][(len(V)-context.interval):].mean()
                volumeHour = V[stock][:(len(V)-context.interval)-1].mean()
                volumeChange = (volumeCurrent - volumeHour) / volumeHour * 100
            
                #print(volumeCurrent, volumeHour, volumeChange)
               
                # Buy stocks
                if (pctChange2 < -0.04 and pctChange > -0.02 and volumeChange > 30):
                    order_target_value(stock, 10000)
                    print(str(stock.symbol) + ' purchased')
                # Sell stocks
                
                ltChange = (priceCurrent - LP[stock][0])/LP[stock][0]
                # log.info('Price two hours ago: ' + str(LP[stock][0]))
                log.info('change over past three hours: ' + str(ltChange))
                # lt price pattern matched w/ high volume suggest trend reversal
                # NOTE: thresholds are arbitrary - no intuition here
                if (ltChange > 0.4 and volumeChange > 15):
                    order_target_value(stock, -5000)
                    print(str(stock.symbol) + ' sold')
                
                elif (ltChange < 0.4 and volumeChange > 15):
                    order_target_value(stock, 10000)
                    print(str(stock.symbol) + ' purchased')
                #TODO: sell at ~2% gain (have been testing with .75-1%)
                #stop order
                
                    
                        
                """
                elif (ltChange > 0.04 and volumeChange > 30):
                    order_target_value(stock, -5000)
                    print(str(stock.symbol) + ' sold')
                
                
                elif (pctChange2 > 0.04 and pctChange < 0.02):
                    order_target_value(stock, -5000)
                    print(str(stock.symbol) + ' sold')
                    """
            
    