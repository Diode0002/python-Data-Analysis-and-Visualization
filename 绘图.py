import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re
from pyecharts import options as opts
from pyecharts.charts import Calendar
from scipy.interpolate import make_interp_spline
from pyecharts.charts import Tab

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 读取数据
df = pd.read_csv('邯郸市24年农业气象数据.csv').iloc[:,1:]
df['日期'] = pd.to_datetime(df['日期'])
df['年份'] = df['日期'].dt.year
df['月份'] = df['日期'].dt.month
df['日'] = df['日期'].dt.day
df['年内天数'] = df['日期'].dt.dayofyear

# 正则提取风力等级
def extract_wind_speed(wind_str):
    match = re.search(r'(\d+)级', str(wind_str))
    return int(match.group(1)) if match else 0
df['风力等级'] = df['风力风向'].apply(extract_wind_speed)

print("数据基本信息：")
print(df[['日期', '天气', '风力风向', '风力等级', '最低温度', '最高温度', '平均温度']].head())
print(f"数据时间范围：{df['日期'].min()} 至 {df['日期'].max()}")
print(f"包含年份：{df['年份'].unique()}")

"""1. 温度趋势折线图（2024年全年）"""
plt.figure(figsize=(12, 6))
# 按日期排序
df_sorted = df.sort_values('日期')
# 绘制最低/最高/平均温度三条线
plt.plot(df_sorted['日期'], df_sorted['最低温度'], label='最低温度', color='blue', alpha=0.7)
plt.plot(df_sorted['日期'], df_sorted['最高温度'], label='最高温度', color='red', alpha=0.7)
plt.plot(df_sorted['日期'], df_sorted['平均温度'], label='平均温度', color='green', linewidth=2)

plt.title('2024年邯郸市温度变化趋势', fontsize=14)
plt.xlabel('日期')
plt.ylabel('温度 (°C)')
plt.grid(linestyle='--', alpha=0.5)
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('温度趋势图.png')
plt.show()
"""2. 月度温度分布箱线图"""
plt.figure(figsize=(12, 8))
sns.boxplot(x='月份', y='平均温度', data=df)
sns.stripplot(x='月份', y='平均温度', data=df, color='black', size=2, jitter=True, alpha=0.3)
plt.title('2024年邯郸市各月平均温度分布', fontsize=14)
plt.xlabel('月份')
plt.ylabel('平均温度 (°C)')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('月度温度分布箱线图.png')
plt.show()


"""3. 温度与降水量关系散点图"""
plt.figure(figsize=(10, 6))
sc = plt.scatter(df['平均温度'], df['降水(mm)'],
                c=df['湿度(%)'], cmap='viridis', alpha=0.6, s=df['风力等级']*5)
plt.colorbar(sc, label='湿度 (%)')
plt.title('温度与降水量关系（点大小表示风力等级）', fontsize=14)
plt.xlabel('平均温度 (°C)')
plt.ylabel('降水量 (mm)')
plt.grid(linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('温度与降水量关系散点图.png')
plt.show()

"""4. 四季气象指标雷达图"""
def get_season(month):
    if month in [3,4,5]:
        return '春季'
    elif month in [6,7,8]:
        return '夏季'
    elif month in [9,10,11]:
        return '秋季'
    else:
        return '冬季'

df['季节'] = df['月份'].apply(get_season)
season_data = df.groupby('季节')[['平均温度', '降水(mm)', '湿度(%)', '风力等级']].mean().reset_index()
categories = season_data.columns[1:].tolist()
N = len(categories)
angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
angles += angles[:1]

fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
for i in range(len(season_data)):
    values = season_data.iloc[i, 1:].tolist()
    values += values[:1]
    ax.plot(angles, values, linewidth=2, label=season_data.iloc[i, 0])
    ax.fill(angles, values, alpha=0.25)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories)
ax.set_title('2024年邯郸市四季气象指标对比', fontsize=14)
ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))
plt.tight_layout()
plt.savefig('四季气象指标雷达图.png')
plt.show()


"""5. 月度降水量柱状图"""
monthly_precip = df.groupby('月份')['降水(mm)'].sum().reset_index()
plt.figure(figsize=(12, 6))
sns.barplot(x='月份', y='降水(mm)', data=monthly_precip, palette='Blues_d')
plt.title('2024年邯郸市各月降水量', fontsize=14)
plt.xlabel('月份')
plt.ylabel('降水量 (mm)')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('月度降水量柱状图.png')
plt.show()

"""6. 2024年温度波形图"""
x_original = df['年内天数']
y_original = df['平均温度']
x_smooth = np.linspace(x_original.min(), x_original.max(), 300)
spline = make_interp_spline(x_original, y_original, k=2)
y_smooth = spline(x_smooth)
plt.figure(figsize=(12, 6))
plt.plot(x_smooth, y_smooth, color='orange', alpha=0.8, label='平均温度')

plt.title('2024年邯郸市温度变化波形', fontsize=14)
plt.xlabel('一年中的第几天')
plt.ylabel('平均温度 (°C)')
plt.legend()
plt.grid(linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('2024年温度波形图.png')
plt.show()


"""7. 2024年温度日历图"""
year_data = df[df['年份'] == 2024]
# 强制转换日期格式为标准的YYYY-MM-DD
year_data['日期_str'] = year_data['日期'].dt.strftime('%Y-%m-%d')
print(year_data)
# 构造日历图数据列表，确保每个元素是[日期, 温度]的格式
data_temp = year_data[['日期_str', '平均温度']].values.tolist()
data_rain = year_data[['日期_str', '降水(mm)']].values.tolist()
tc = (
    Calendar(init_opts=opts.InitOpts(width="900px", height="500px"))
    .add(
        "平均温度",
        yaxis_data=data_temp,
        calendar_opts=opts.CalendarOpts(
            range_="2024",
            daylabel_opts=opts.CalendarDayLabelOpts(name_map="cn"),
            monthlabel_opts=opts.CalendarMonthLabelOpts(name_map="cn"),
        ),
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(title="2024年邯郸市温度日历图"),
        visualmap_opts=opts.VisualMapOpts(
            max_=45,
            min_=-10,
            range_text=["高温", "低温"],
            orient="horizontal",
            pos_top="230px",
            pos_left="center",
            range_color=["#00f", "#0ff", "#0f0", "#ff0", "#f00"],
        ),
        tooltip_opts=opts.TooltipOpts(formatter="{c} °C"),
    )
)
rc = (
    Calendar(init_opts=opts.InitOpts(width="900px", height="500px"))
    .add(
        series_name="降水量",
        yaxis_data=data_rain,
        calendar_opts=opts.CalendarOpts(
            range_="2024",
            daylabel_opts=opts.CalendarDayLabelOpts(name_map="cn"),
            monthlabel_opts=opts.CalendarMonthLabelOpts(name_map="cn"),
        ),
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(title="2024年降水日历图"),
        visualmap_opts=opts.VisualMapOpts(
            max_=50,
            min_=0,
            orient="horizontal",
            pos_top="230px",
            pos_left="center",
            range_color=["#f7fbff", "#c6dbef", "#6baed6", "#2171b5", "#08306b"]

        ),
        tooltip_opts=opts.TooltipOpts(formatter="{a}<br/>{b}: {c}mm"),
    )
)
rc.render("降水.html")
tc.render("气温.html")
"""8. 日照时长月度变化"""
monthly_sunshine = df.groupby('月份')['日照时长(h)'].mean().reset_index()

plt.figure(figsize=(12, 6))
plt.bar(monthly_sunshine['月份'], monthly_sunshine['日照时长(h)'],
        color='gold', alpha=0.7, label='平均日照时长')
plt.plot(monthly_sunshine['月份'], monthly_sunshine['日照时长(h)'],
         color='darkorange', linewidth=2, marker='o', label='变化趋势')

plt.title('2024年邯郸市各月平均日照时长变化', fontsize=14)
plt.xlabel('月份')
plt.ylabel('日照时长 (小时)')
plt.xticks(range(1, 13))
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend()
plt.tight_layout()
plt.savefig('月度日照时长变化图.png')
plt.show()

"""9. 日照时长与温度散点图"""
plt.figure(figsize=(10, 6))
sc = plt.scatter(df['平均温度'], df['日照时长(h)'],
                c=df['月份'], cmap='viridis', alpha=0.7, s=50)
plt.colorbar(sc, label='月份')
plt.title('日照时长与平均温度关系', fontsize=14)
plt.xlabel('平均温度 (°C)')
plt.ylabel('日照时长 (小时)')
plt.grid(linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('日照时长与温度关系图.png')
plt.show()

"""10. 日照时长与降水量关系分析"""
plt.figure(figsize=(10, 6))
sc = plt.scatter(df['降水(mm)'], df['日照时长(h)'],
                c=df['平均温度'], cmap='coolwarm', alpha=0.7, s=50)
plt.colorbar(sc, label='平均温度 (°C)')
plt.title('日照时长与降水量关系', fontsize=14)
plt.xlabel('降水量 (mm)')
plt.ylabel('日照时长 (小时)')
plt.grid(linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('日照时长与降水量关系图.png')
plt.show()

"""11. 日照时长季节性分析"""
season_sunshine = df.groupby('季节')['日照时长(h)'].agg(['mean', 'std']).reset_index()
plt.figure(figsize=(10, 6))
bars = plt.bar(season_sunshine['季节'], season_sunshine['mean'],
               color=['lightgreen', 'coral', 'gold', 'lightblue'],
               alpha=0.7, yerr=season_sunshine['std'], capsize=5)
plt.title('2024年邯郸市四季平均日照时长', fontsize=14)
plt.xlabel('季节')
plt.ylabel('平均日照时长 (小时)')
plt.grid(axis='y', linestyle='--', alpha=0.7)
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
             f'{height:.1f}', ha='center', va='bottom')

plt.tight_layout()
plt.savefig('四季日照时长分析图.png')
plt.show()
# 计算相关系数
correlation_temp = df['日照时长(h)'].corr(df['平均温度'])
correlation_rain = df['日照时长(h)'].corr(df['降水(mm)'])
print(f"日照时长与平均温度的相关系数: {correlation_temp:.3f}")
print(f"日照时长与降水量的相关系数: {correlation_rain:.3f}")

