import pandas as pd
import numpy as np

#数据预处理
dff= []
for i in range(12):
    filename = f'weather_data ({i}).xlsx'
    df = pd.read_excel(filename, header=None)
    dff.append(df)
columnames=["日期","天气","风力风向","最低温度","最高温度","平均温度","湿度(%)","降水(mm)","日照时长(h)","短波辐射总量"]
dataa=dff
for i in range(len(dataa)):
    dataa[i]=dataa[i].iloc[3:,[0,1,2,3,4,5,9,10,11,12]]
data=dataa[0]
for i in range(1,12):
    data=pd.concat([data, dataa[i]], ignore_index=True)
data.columns=columnames

data['日期'] = pd.to_datetime(data['日期'])
start_date = '2024-01-01'
end_date = '2024-12-31'
dayfull = pd.date_range(start=start_date, end=end_date, freq='D')
dffull = pd.DataFrame({'日期': dayfull})
datae = pd.merge(dffull, data, on='日期', how='left')
data = datae.fillna(method='bfill')
print(f"合并后数据天数: {len(data)}")
print(data)
data.to_csv('邯郸市24年农业气象数据.csv')