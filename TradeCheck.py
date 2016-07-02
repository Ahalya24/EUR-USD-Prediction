# -*- coding: utf-8 -*-
"""
Created on Tue May 12 13:25:06 2015

@author: Ahalya
"""

import os
import pandas as pd
ewma= pd.stats.moments.ewma
from sklearn import linear_model
import numpy as np

os.chdir("C:/Users/Ahalya/Desktop/April/Forex")

target = open('EURUSD_Daily_Rates_2015.csv','a')
src = open('Daily_Data.csv','r') # place only in order OPEN,HIGH,LOW, CLOSE
lines = src.readlines()
target.write(lines[1])
target.close()

data = pd.read_csv("EURUSD_Daily_Rates.csv",index_col = 'DATE', parse_dates=True)
op = data['OPEN']
cl = data['CLOSE']
hg = data['HIGH']
lw = data['LOW']
ind = data.index
op_ewma = ewma(op,span=2)
cl_ewma = ewma(cl,span=2)
hg_ewma = ewma(hg,span=2)
lw_ewma = ewma(lw,span=2)

clf = linear_model.LinearRegression()

clf.fit(op_ewma[:,np.newaxis],op)
today_open = lines[2]
to = today_open.split(",")
op_pred = clf.predict(float(to[1]))

yest = lines[1]
yest = yest.split(",")
clf.fit(cl_ewma[:,np.newaxis],cl)
cl_pred = clf.predict(float(yest[4]))

clf.fit(hg_ewma[:,np.newaxis],hg)
hg_pred = clf.predict(float(yest[2]))

clf.fit(lw_ewma[:,np.newaxis],lw)
lw_pred = clf.predict(float(yest[3]))

src.close()

print(op_pred,hg_pred,lw_pred,cl_pred)
df = pd.DataFrame({'Tomo OPEN':op_pred,'Today HIGH':hg_pred,'Today Close':cl_pred,'Today Low':lw_pred,}) 
output = open("predicted.csv",'w')
df.to_csv(output,sep =",")
output.close()
