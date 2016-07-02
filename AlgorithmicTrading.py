# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 21:20:20 2015

@author: Ahalya

"""

import os
import pandas as pd
ewma= pd.stats.moments.ewma
from sklearn import linear_model
import numpy as np
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from math import sqrt
import smtplib
import schedule
import time


os.chdir(".../Forex")


target = open('EURUSD_Daily_Rates_2015.csv','a')
src = open('Daily_Data.csv','r')
lines = src.readlines()
target.write(lines[1])
target.close()
src.close()

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
clf.fit(cl_ewma[:,np.newaxis],cl)
clf.fit(hg_ewma[:,np.newaxis],hg)
clf.fit(lw_ewma[:,np.newaxis],lw)

op_pred=[0]
cl_pred=[0]
hg_pred=[0]
lw_pred=[0]

for i in range(1,op_ewma.shape[0]):
    op_pred.append((str(clf.predict(op_ewma[i])).replace("[","")).replace(']',''))
    cl_pred.append((str(clf.predict(cl_ewma[i])).replace("[","")).replace(']',''))    
    hg_pred.append((str(clf.predict(hg_ewma[i])).replace("[","")).replace(']',''))    
    lw_pred.append((str(clf.predict(lw_ewma[i])).replace("[","")).replace(']',''))
 

rec_action = [0]
profit=[0]

l = len(op_ewma)


for i in range(0,l-1):
    if (float(op[i])<float(op_pred[i+1])):    
        rec_action.append("BUY")
        if(float(hg[i])>float(hg_pred[i])):
            p = float(hg_pred[i]) - op[i]
        else:
            p = cl[i]-op[i]
    else:
        rec_action.append("SELL")
        if(float(lw[i])>float(lw_pred[i])):
            p = float(op[i]) - float(lw_pred[i])
        else:
            p = op[i] - cl[i]
    profit.append(p)
    
df = pd.DataFrame({'Date':ind,'Actual Open':op,'EWMA Open':op_ewma,'Predicted Open':op_pred,'Actual Close':cl,'Predicted Close':cl_pred,'Actual High':hg,'Predicted High':hg_pred,'Actual Low':lw,'Predicted Low':lw_pred,'Recommended Action':rec_action,'Profit Made':profit}) 
df = df.set_index(['Date'])
output = open("outputewma2015.csv",'w')
df.to_csv(output,sep =",")
output.close()

#calculate RSME
datap = pd.read_csv(open("outputewma2015.csv",'r'), index_col = 'Date', parse_dates = True)
datap = datap.drop(df.head(1).index)

def calc_RSME(act,pre):
    rmse_calc = sqrt(mean_squared_error(act,pre))
    return round(rmse_calc,5)

print("Open RMSE:",calc_RSME(datap['Actual Open'],datap['Predicted Open']))
print("Close RMSE:",calc_RSME(datap['Actual Close'],datap['Predicted Close']))
print("High RMSE:",calc_RSME(datap['Actual High'],datap['Predicted High']))
print("Low RMSE:",calc_RSME(datap['Actual Low'],datap['Predicted Low']))
print(r2_score(datap['Actual Low'],datap['Predicted Low']))

#datap['Actual Open'].tail(15).plot()
#datap['Predicted Open'].tail(15).plot()

#values to suggest user
update_file = pd.read_csv(open('Daily_Data.csv','r'))
update_val = update_file.values
today_actual_open = update_val[1,1]

pred_file = pd.read_csv(open('outputewma2015.csv','r'))
pred_val = pred_file.values
l = len(pred_val) - 1

today_pred_open = pred_val[l,9]
today_pred_low = pred_val[l,8]
today_pred_high = pred_val[l,7]
today_pred_close = pred_val[l,6]
tomo_pred_open = clf.predict(today_actual_open)
if (today_actual_open<tomo_pred_open):
    action = "BUY"
else:
    action="SELL"
#compose email message
OPMSG = ""
OPMSG += "<b><u>Today's Prediction:</u></b><br>"
OPMSG += "Today's Open price is:"+ str(today_actual_open)+"<br><br>"
OPMSG += "Today's High price will be:"+ str(today_pred_high)+"<br>"
OPMSG += "Today's Low price will be:"+ str(today_pred_low)+"<br>"
OPMSG += "Tomorrow's Open price will be:"+ str(tomo_pred_open)+"<br><br>"
OPMSG += "Recommended Action:<b>"+ action+"</b><br><br><br>"
l = len(pred_val)
OPMSG += "<b><u>Weekly Overview:</u></b><br><br>"
OPMSG += "<table border = 1><tr><td><b>DATE</b></td><td><b>ACTION</b></td><td><b>PROFIT</b></td></b></tr>"
for i in range((l-5),l):
    OPMSG += "<tr><td>"+pred_val[i,0]+"</td><td>"+str(pred_val[i,11])+"</td><td>"+str(round(((pred_val[i,10]-.0005)*100000),2))+"</td></tr>"
OPMSG += "</table>"


#send email to user
class Gmail(object):
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.server = 'smtp.gmail.com'
        self.port = 587
        session = smtplib.SMTP(self.server, self.port)        
        session.ehlo()
        session.starttls()
        session.ehlo
        session.login(self.email, self.password)
        self.session = session

    def send_message(To, subject, body):
        
        headers = [
            "From: " + To.email,
            "Subject: " + subject,
            "To: " + To.email,
            "MIME-Version: 1.0",
           "Content-Type: text/html"]
        headers = "\r\n".join(headers)
        To.session.sendmail(
            To.email,
            To.email,
            headers + "\r\n\r\n" + body)

gm = Gmail('XXX@YY.COM', 'xxxxxx')
subject = 'EUR-USD Prediction'
#gm.send_message(subject, OPMSG)



def job():
    gm.send_message(subject, OPMSG)
    print("I am working..")

schedule.every(24).hours.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)

