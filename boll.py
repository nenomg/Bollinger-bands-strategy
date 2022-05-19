# -*- coding: utf-8 -*-
"""
Created on Thu May 19 17:50:55 2022

@author: Eugenio Menacho de Góngora
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



#Calculates the bollinger bands based on the typical price 
#((High + Low + Close)/3)

#Input: 
#data: Dataset
#m: Number of days
#n: Standart deviation
def bollingerBands(data, m, n):
    res = []
    res2 = []
    j = 0
    for i in range(m, len(data)):
        tp = ((data.Close[j:i] + data.High[j:i] + data.Low[j:i]) / 3)
        
        res.append(np.mean(tp) + n * np.std(tp))
        res2.append(np.mean(tp) - n * np.std(tp))
        j = j + 1
    
    return res, res2

#Plot the bollinger bands and the price
def plotBoll(data, b_u, b_d):
    plt.ylabel('Price')
    plt.plot(np.arange(0,200), b_d[0:200], label="down")
    plt.plot(np.arange(0,200), b_u[0:200], label="up")
    plt.plot(data["Close"][0:200], label="price")
    plt.legend()
    plt.title('Bollinger bands for first 200')
    plt.show()

#Plot the bollinger bands, the price and the buys and sells
def plotBuysAndSells(b_d, b_u, price, name, m, smoothing, buys_idx, sells_idx):
    
    margin_d = 0
    margin_u = 300
    
    buys = []
    buys_p = []
    for i in range(0, len(buys_idx)):
        if buys_idx[i] >= margin_d and buys_idx[i]<=margin_u:
            buys.append(price[buys_idx[i]])
            buys_p.append(buys_idx[i])
    sells = []
    sells_p = []
    for i in range(0, len(sells_idx)):
        if sells_idx[i] >= margin_d and sells_idx[i]<=margin_u:
            sells.append(price[sells_idx[i]])
            sells_p.append(sells_idx[i])
    
    
    
    plt.ylabel('Price')
    plt.plot(np.arange(margin_d,margin_u), b_u[margin_d:margin_u], label="up")
    plt.plot(np.arange(margin_d,margin_u), b_d[margin_d:margin_u], label="down")
    plt.plot(price[margin_d:margin_u], label="price")
    
    
    plt.scatter(buys_p, buys,s = 30, marker='o', c="red")
    plt.scatter(sells_p, sells,s=30, marker='o', c="blue")
    
    plt.legend()
    plt.title('Bollinger bands for first 200 [' + name + '] m = ' + str(m) + ", smoothing = "+ str(smoothing))
    plt.show()






#Read the dataset, obtained using the binance API
data = pd.read_csv("BTCEUR_4HOUR.csv",low_memory=False, names = ["Date","Open","High", "Low", "Close", "Vol","quote_asset_volume", "num_trades", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume"]);
data = data[1::]
data = data.reset_index(drop=True)

#Convert the dataset to numeric
data[["Open","High", "Low", "Close", "Vol","quote_asset_volume", "num_trades", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume"]] = data[["Open","High", "Low", "Close", "Vol","quote_asset_volume", "num_trades", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume"]].apply(pd.to_numeric)

#Print the first 5 rows of the dataset
print("------------------------------- 1. DATASET -------------------------------\n")
print(data.head())
print("\nShape: ", data.shape)

#Define the variables for the bollinger bands
m = 12
smoothing = 2

#Calculate the bollinger bands
print("\n------------------------------- 2. Calculating bollinger bands -------------------------------\n")
b_u, b_d = bollingerBands(data, m, smoothing)

#Get rid of the m rows deleted in the bollinger bands
data = data[m:len(data)]
data = data.reset_index(drop=True)

print("\n------------------------------- 3. Plot bollinger bands -------------------------------\n")
#Plot the bollinger bands
plotBoll(data, b_u, b_d)


print("\n------------------------------- 4. Begin strategy -------------------------------\n")

#It begins the strategy in sells_idx we store the index of the sells that where made
#The same with buys_idx and in percentages I store the percentage won after the sell

buys_idx = []
sells_idx = []

prev_price = -1
d_band = False
u_band = False
buy = False
d_band2 = False
sell = False
res = 0
percentages = []
            
            
for i in range(0, len(data)):
    #When it crosses with the band down and it hasn't bought it activates d_band
    if data.iloc[i]["Close"] < b_d[i] and d_band == False and u_band == False and buy == False:
        d_band = True
    
    
    #If it crosses again with the band down and d_band is activated it buys
    elif data.iloc[i]["Close"] > b_d[i] and d_band == True and buy == False:
        prev_price = data.iloc[i]["Close"]
        buy = True
        d_band = False
        sell = False
        buys_idx.append(i)
    
    #When it crosses up for first time it activates u_band
    elif data.iloc[i]["Close"] > b_u[i] and u_band == False and d_band == False and buy == True:
        u_band = True
                    
    #If u_band is activated and it crosses again with the upper band it sells
    elif data.iloc[i]["Close"] < b_u[i] and u_band == True and buy == True and sell == False:
        res = res + ((data.iloc[i]["Close"] - prev_price) / prev_price)
        percentages.append((data.iloc[i]["Close"] / prev_price))
        buy = False
        u_band = False
        sell = True
        prev_price = -1
        sells_idx.append(i)

print("\n------------------------------- 5. Plot buys and sells -------------------------------\n")
plotBuysAndSells(b_d, b_u, data["Close"], "BTC", m, smoothing, buys_idx, sells_idx)


print("\n------------------------------- 6. Calculate results without binance taxes -------------------------------\n")
unidad = 1
for i in range(0, len(percentages)):
  unidad = unidad * percentages[i]

print("m = ",m, "| smoothing = ",  smoothing, "| Unit: 1 ->", unidad)


print("\n------------------------------- 7. Calculate results with binance taxes -------------------------------\n")
print("Considering an inversion of 500$ to start and taxes of 0.4$ for each trade\n")
unidad = 500
for i in range(0, len(percentages)):
  unidad = unidad * percentages[i] - 0.40;

print("m = ",m, "| smoothing = ",  smoothing, "| 500 ->", unidad)
