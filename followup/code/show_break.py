import pandas as pd
pd.set_option("display.width",250)
m=pd.read_csv('tables/break_monthly.csv')
for col,lo,hi,cols in [('r1659_mean','2014-01','2016-03',None),('r1659_t','2014-06','2015-12',None),('zero1659','2014-01','2016-01',['EURUSD','USDJPY','AUDUSD','GBPUSD']),('rng1659','2014-01','2016-01',['EURUSD','USDJPY','AUDUSD','GBPUSD']),('rng_pre','2014-06','2015-06',['EURUSD','USDJPY','AUDUSD','GBPUSD']),('dec_mean','2014-06','2016-01',['EURUSD','USDJPY','AUDUSD','GBPUSD'])]:
    p=m.pivot(index='ym',columns='pair',values=col).round(2).loc[lo:hi]
    if cols: p=p[cols]
    print('##',col); print(p.to_string())
