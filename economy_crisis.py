#Files raw_data_1.csv, raw_data_2.csv i raw_data_3.xlsx were taken from:
#https://databank.worldbank.org/,
#https://unstats.un.org/UNSDWebsite/
#https://datahelpdesk.worldbank.org/knowledgebase/articles/906519-world-bank-country-and-lending-groups.

import numpy as np
import pandas as pd
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

## Preparing data to further analysis
df1 = pd.read_csv('raw_data_1.csv')
df1 = df1[:-7]
df1 = df1.set_index('Country Code')
df1 = df1.rename(columns={'2006 [YR2006]': '2006',
                        '2007 [YR2007]': '2007',
                         '2008 [YR2008]': '2008',
                         '2009 [YR2009]': '2009',
                         '2010 [YR2010]': '2010',
                         '2011 [YR2011]': '2011'})


df1 = df1.drop(columns=df1.columns.difference(['Country Name', '2006', '2007', '2008', '2009', '2010', '2011']))
df1 = df1.replace('..', np.nan)
#display(df1)

df2=pd.read_csv('raw_data_2.csv',sep=';')
df2 = df2.set_index('ISO-alpha3 Code')
df2.index.name='Country Code'
df2=df2.loc[:,['Region Name']]
#display(df2)

df3 =pd.read_excel('raw_data_3.xlsx', sheet_name='Country Analytical History', header=5)
df3 = df3.drop(df3.index[:5])
df3.columns = df3.columns.astype(str)
df3 = df3.rename(columns={'Unnamed: 0': 'Country Code',
                        'Data for calendar year :': 'Country Name',
                         '2008':'Income Group'})
df3 = df3[:-4]
df3 = df3.loc[:, ['Country Code','Income Group']]
df3['Income Group'] = df3['Income Group'].replace({'H': 'High', 'UM': 'Upper middle', 'LM': 'Lower middle', 'L': 'Low'})
df3 = df3.set_index('Country Code')
df3 = df3.replace('..', np.nan)
#display(df3)

df_merged = df2.join(df3)
df_merged = df_merged.join(df1)
kolumna_trzecia = df_merged.pop('Country Name')
df_merged.insert(0, 'Country Name', kolumna_trzecia)

df_cleaned = df_merged.dropna()
df_cleaned = df_cleaned.drop(df_cleaned[df_cleaned.index == 'LBY'].index)

#display(df_cleaned)
#for problems with types: 'object' zamiast 'float' lub 'int'
numeric_columns = ['2006', '2007', '2008', '2009', '2010', '2011']
df_cleaned[numeric_columns] = df_cleaned[numeric_columns].apply(pd.to_numeric, errors='coerce')
#recession_data_1.info()

recession_data_1=df_cleaned
recession_data_1.to_pickle('recession_data_1.pkl')


pd.concat([recession_data_1.head(5), recession_data_1.tail(5)]).style.format(precision=2)


## Grouping data into intervals for GDP

recession_data_1 = pd.read_pickle("recession_data_1.pkl")

intervals = pd.IntervalIndex.from_breaks(range(-20, 36, 5), closed='right')
recession_table_1 = pd.DataFrame(index=recession_data_1.columns[3:], columns=intervals)

for Year in recession_table_1.index:
    for interval in intervals:
        values = recession_data_1[Year]
        count = ((values > interval.left) & (values <= interval.right)).sum()
        recession_table_1.loc[Year, interval] = count

recession_table_1 /= len(recession_data_1)
recession_table_1.index.name = 'Year'

recession_rounded = recession_table_1.style.format(precision=2)


regions = recession_data_1["Region Name"].unique()
years = recession_data_1.columns[3:]
intervals = pd.interval_range(start=-20, end=35, freq=5, closed="right")

interval_index = pd.IntervalIndex(intervals)

recession_table_2 = pd.DataFrame(index=pd.MultiIndex.from_product([regions, years]), columns=interval_index)

for region in regions:
    region_data = recession_data_1[recession_data_1["Region Name"] == region]
    region_obs_count = len(region_data)
    for year in years:
        values = region_data[year]
        for interval in interval_index:
            count = ((values > interval.left) & (values <= interval.right)).sum()
            recession_table_2.loc[(region, year), interval] = count / region_obs_count

recession_table_2.index.names = ['Region Name', 'Year']
recession_rounded_2 = recession_table_2.style.format(precision=2)


income_groups = recession_data_1["Income Group"].unique()
years = recession_data_1.columns[3:]
intervals = pd.interval_range(start=-20, end=35, freq=5, closed="right")

interval_index = pd.IntervalIndex(intervals)

recession_table_3 = pd.DataFrame(index=pd.MultiIndex.from_product([income_groups, years]), columns=interval_index)

for income_group in income_groups:
    group_data = recession_data_1[recession_data_1["Income Group"] == income_group]
    group_obs_count = len(group_data)
    for year in years:
        values = group_data[year]
        for interval in interval_index:
            count = ((values > interval.left) & (values <= interval.right)).sum()
            recession_table_3.loc[(income_group, year), interval] = count / group_obs_count

recession_table_3.index.names = ['Income Group', 'Year']
income_order = ["Low", "Lower middle", "Upper middle", "High"]
recession_table_3 = recession_table_3.reindex(income_order, level='Income Group')
recession_rounded_3 = recession_table_3.style.format(precision=2)

#Visualisation of data:

bins = np.arange(-25, 45, 5)
COLOR_DICT = {
    "2006": "slategray",
    "2007": "magenta",
    "2008": "darkgoldenrod",
    "2009": "crimson",
    "2010": "royalblue",
    "2011": "darkgreen"
}

def plot_frequency_chart(ax, data, title):
    ax.set_facecolor("white")
    for year in range(2006, 2012):
        sns.histplot(data[str(year)], color=COLOR_DICT[str(year)], ax=ax, element="poly", fill=False, stat="probability", bins=bins, label=str(year))
    ax.grid(True)
    ax.set_xlim([-20, 35])
    ax.set_ylim([0, 1])
    ax.set_title(title)
    ax.set_ylabel("Częstość")
    ax.set_xlabel("GDP growth indicator (annual %)")
    ax.legend(title="Year")

fig, ax = plt.subplots(2, 5, figsize=(18, 10), facecolor="white")

plot_frequency_chart(ax[0, 0], recession_data_1, "All data")
plot_frequency_chart(ax[0, 1], recession_data_1[recession_data_1["Income Group"] == "Low"], "Income Group - Low")
plot_frequency_chart(ax[0, 2], recession_data_1[recession_data_1["Income Group"] == "Lower middle"], "Income Group - Lower middle")
plot_frequency_chart(ax[0, 3], recession_data_1[recession_data_1["Income Group"] == "Upper middle"], "Income Group - Upper middle")
plot_frequency_chart(ax[0, 4], recession_data_1[recession_data_1["Income Group"] == "High"], "Income Group - High")

region_names = recession_data_1["Region Name"].unique()

for i, region_name in enumerate(region_names):
    plot_frequency_chart(ax[1, i], recession_data_1[recession_data_1["Region Name"] == region_name], f"Region Name - {region_name}")

fig.suptitle("Frequency Diagrams")

#BOXPLOTS
# Boxplot
def plot_boxplot(ax, data, title, color=None, hue=None, palette=None):
    sns.boxplot(data=data, x="variable", y="value", ax=ax, color=color, hue=hue, palette=palette, showmeans=True,
                meanprops={"marker":"o","markerfacecolor":"white", "markeredgecolor":"black","markersize":"10"})
    ax.set_title(title)
    ax.set_ylabel("GPD growth (annual %)")
    ax.set_xlabel("Year")
    ax.set_ylim(-25, 40)
    ax.axhline(y=0, color="red")
    ax.grid(True)
    ax.set_facecolor("white")

df_all = pd.melt(recession_data_1, value_vars=recession_data_1.columns[3:])
df_income = pd.melt(recession_data_1, id_vars=["Income Group"], value_vars=recession_data_1.columns[3:])
income_order = ["Low", "Lower middle", "Upper middle", "High"]
df_income["Income Group"] = pd.Categorical(df_income["Income Group"], categories=income_order, ordered=True)
df_region = pd.melt(recession_data_1, id_vars=["Region Name"], value_vars=recession_data_1.columns[3:])
fig, ax = plt.subplots(3, 1, figsize=(20, 20), facecolor="white")

plot_boxplot(ax[0], df_all, "All data", color="pink")

plot_boxplot(ax[1], df_income, "Income Groups", hue="Income Group", palette="coolwarm")
ax[1].legend(title="Income Group", ncol=4)


olympic_colors_palette = {
    "Africa": "dimgray",
    "Asia": "navajowhite",
    "Europe": "lightblue",
    "Oceania" :  "lightgreen",
    "Americas" : "lightcoral"
}

plot_boxplot(ax[2], df_region, "Region Name", hue="Region Name", palette=olympic_colors_palette)
ax[2].legend(title="Region Name", ncol=5)

fig.suptitle("Boxplots, divided by:")
plt.show()

#SWARMPLOTS
# Swarmplot
def plot_swarmplot(ax, data, title, color=None, hue=None, palette=None, dodge=False):
    sns.swarmplot(data=data, x="variable", y="value", ax=ax, color=color, hue=hue, palette=palette, dodge=dodge)
    ax.set_title(title)
    ax.set_ylabel("GPD growth (annual %)")
    ax.set_xlabel("Year")
    ax.set_ylim(-25, 40)
    ax.axhline(y=0, color="red")
    ax.grid(True)
    ax.set_facecolor("white")

df_all = pd.melt(recession_data_1, value_vars=recession_data_1.columns[3:])
df_income = pd.melt(recession_data_1, id_vars=["Income Group"], value_vars=recession_data_1.columns[3:])
income_order = ["Low", "Lower middle", "Upper middle", "High"]
df_income["Income Group"] = pd.Categorical(df_income["Income Group"], categories=income_order, ordered=True)
df_region = pd.melt(recession_data_1, id_vars=["Region Name"], value_vars=recession_data_1.columns[3:])

fig, ax = plt.subplots(3, 1, figsize=(20, 20), facecolor="white")

plot_swarmplot(ax[0], df_all, "All data", color="pink")

plot_swarmplot(ax[1], df_income, "Income Groups", hue="Income Group", palette="coolwarm", dodge=True)
ax[1].legend(title="Income Group", ncol=4)

olympic_colors_palette = {
    "Africa": "dimgray",
    "Asia": "navajowhite",
    "Europe": "lightblue",
    "Oceania" :  "lightgreen",
    "Americas" : "lightcoral"
}
plot_swarmplot(ax[2], df_region, "Region Name", hue="Region Name",palette=olympic_colors_palette, dodge=True)
ax[2].legend(title="Region Name", ncol=5)

fig.suptitle("Swarmplots, divided by:")
plt.show()

#VIOLINPLOTS

# Violinplot
def plot_violinplot(ax, data, title, color=None, hue=None, palette=None):
    sns.violinplot(data=data, x="variable", y="value", ax=ax, color=color, hue=hue, palette=palette, inner="quartile")
    ax.set_title(title)
    ax.set_ylabel("GPD growth (annual %)")
    ax.set_xlabel("Year")
    ax.set_ylim(-25, 40)
    ax.axhline(y=0, color="red")
    ax.grid(True)
    ax.set_facecolor("white")

df_all = pd.melt(recession_data_1, value_vars=recession_data_1.columns[3:])
df_income = pd.melt(recession_data_1, id_vars=["Income Group"], value_vars=recession_data_1.columns[3:])
income_order = ["Low", "Lower middle", "Upper middle", "High"]
df_income["Income Group"] = pd.Categorical(df_income["Income Group"], categories=income_order, ordered=True)
df_region = pd.melt(recession_data_1, id_vars=["Region Name"], value_vars=recession_data_1.columns[3:])

fig, ax = plt.subplots(3, 1, figsize=(20, 20), facecolor="white")

plot_violinplot(ax[0], df_all, "All data", color="pink")

plot_violinplot(ax[1], df_income, "Income Groups", hue="Income Group", palette="coolwarm")
ax[1].legend(title="Income Group", ncol=4)

olympic_colors_palette = {
    "Africa": "dimgray",
    "Asia": "navajowhite",
    "Europe": "lightblue",
    "Oceania" :  "lightgreen",
    "Americas" : "lightcoral"
}
plot_violinplot(ax[2], df_region, "Region Name", hue="Region Name", palette=olympic_colors_palette)
ax[2].legend(title="Region Name", ncol=5)

fig.suptitle("Violinplots, divided by:")
plt.show()

