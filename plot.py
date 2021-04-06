>>> from datetime import datetime
>>> datetime.strptime("2012-may-31 19:00", "%Y-%b-%d %H:%M")
 datetime.datetime(2012, 5, 31, 19, 0)
This is an example of how to plot data once you have an array of datetimes:

import matplotlib.pyplot as plt
import datetime
import numpy as np

x = np.array([datetime.datetime(2013, 9, 28, i, 0) for i in range(24)])
y = np.random.randint(100, size=x.shape)

plt.plot(x,y)
plt.show()

https://stackoverflow.com/questions/19079143/how-to-plot-time-series-in-python
https://towardsdatascience.com/how-to-plot-time-series-86b5358197d6
https://stackoverflow.com/questions/4090383/plotting-unix-timestamps-in-matplotlib
https://plotly.com/python/time-series/
https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html


myDate = "2014.08.01 04:41:04"
timestamp = time.mktime(datetime.datetime.strptime(myDate, "%Y.%m.%d %H:%M:%S").timetuple())

import pandas as pd
import sqlite3

con = sqlite3.connect("data/portal_mammals.sqlite")

# Load the data into a DataFrame
surveys_df = pd.read_sql_query("SELECT * from surveys", con)

# Select only data for 2002
surveys2002 = surveys_df[surveys_df.year == 2002]

# Write the new DataFrame to a new SQLite table
surveys2002.to_sql("surveys2002", con, if_exists="replace")

con.close()

data.to_sql('book_details', con = engine, if_exists = 'append', chunksize = 1000)


import sqlite3
connection = sqlite3.connect('~/foo.sqlite')
cursor = connection.execute('select * from bar')
cursor.description is description of columns

names = list(map(lambda x: x[0], cursor.description))







import sqlite3
from pandas import DataFrame
import plotly.express as px
con = sqlite3.connect('sarDATA/db/redhat_5.db')
cur = con.cursor()
cur.execute("SELECT * FROM 'IORates.1' where name='localhost.localdomain-007f0100'")
#cur.execute("SELECT * FROM 'IORates.1'")
a = cur.fetchall()
df = DataFrame(a,columns=['name', 'date', 'tps', 'wps', 'zps'])
df1 = df.loc[:,"date":"zps"]
df1 = df.columns[1:]
print(df1)
fig = px.line(df, x='date', y=df.columns[2:],
              hover_data={"date": "|%B %d, %Y"},
              title='custom tick labels')

fig.show()
#fig = px.area(df, x='date', y=df.columns[2:], facet_col="name", facet_col_wrap=2)
#fig.show()




------------------------------------------


import sqlite3
from pandas import DataFrame
import plotly.express as px

import numpy as np
import joypy
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import warnings; warnings.filterwarnings(action='once')

large = 22; med = 16; small = 12
params = {'axes.titlesize': large,
          'legend.fontsize': med,
          'figure.figsize': (16, 10),
          'axes.labelsize': med,
          'axes.titlesize': med,
          'xtick.labelsize': med,
          'ytick.labelsize': med,
          'figure.titlesize': large}
plt.rcParams.update(params)
plt.style.use('seaborn-whitegrid')
sns.set_style("white")
%matplotlib inline


con = sqlite3.connect('sarDATA/db/redhat_5.db')
cur = con.cursor()
cur.execute("SELECT * FROM 'IORates.1' where name='localhost.localdomain-007f0100'")
#cur.execute("SELECT * FROM 'IORates.1'")
a = cur.fetchall()
df = DataFrame(a,columns=['name', 'date', 'tps', 'wps', 'zps'])
df1 = df.loc[:,"date":"zps"]
df1 = df.columns[1:]
print(df1)
fig = px.line(df, x='date', y=df.columns[2:],
              hover_data={"date": "|%B %d, %Y"},
              title='custom tick labels')

fig.show()
#fig = px.area(df, x='date', y=df.columns[2:], facet_col="name", facet_col_wrap=2)
#fig.show()

import matplotlib.dates as mdates
myFmt = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')
ax.xaxis.set_major_formatter(myFmt)

# Prepare Data
x = df['date'].values.tolist()
y1 = df['tps'].values.tolist()
y2 = df['zps'].values.tolist()
mycolors = ['tab:red', 'tab:blue', 'tab:green', 'tab:orange', 'tab:brown', 'tab:grey', 'tab:pink', 'tab:olive']      
columns = ['tps', 'zps']

# Draw Plot 
fig, ax = plt.subplots(1, 1, figsize=(16,9), dpi= 80)
ax.fill_between(x, y1=y1, y2=0, label=columns[1], alpha=0.5, color=mycolors[1], linewidth=2)
ax.fill_between(x, y1=y2, y2=0, label=columns[0], alpha=0.5, color=mycolors[0], linewidth=2)

# Decorations
ax.set_title('Personal Savings Rate vs Median Duration of Unemployment', fontsize=18)
ax.set(ylim=[0, 30])
ax.legend(loc='best', fontsize=12)
plt.xticks(x[::50], fontsize=10, horizontalalignment='center')
plt.yticks(np.arange(2.5, 30.0, 2.5), fontsize=10)
plt.xlim(-10, x[-1])

# Draw Tick lines  
for y in np.arange(2.5, 30.0, 2.5):    
    plt.hlines(y, xmin=0, xmax=len(x), colors='black', alpha=0.3, linestyles="--", lw=0.5)

# Lighten borders
plt.gca().spines["top"].set_alpha(0)
plt.gca().spines["bottom"].set_alpha(.3)
plt.gca().spines["right"].set_alpha(0)
plt.gca().spines["left"].set_alpha(.3)
plt.show()
