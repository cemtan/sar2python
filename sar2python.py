import sqlite3
import json
import os
import shutil
import tarfile
from flask import Flask, render_template, request, url_for, flash, redirect, jsonify
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
import altair as alt
import pandas as pd
import numpy as np
from datetime import datetime
from vega_datasets import data
import datetime as dt

def initializeDb ():
    try:
        s2con = sqlite3.connect('data/db/hosts.db') 
        s2cur =  s2con.cursor()
        sqlCommand = '''CREATE TABLE "hosts" (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, os TEXT NOT NULL)'''
        s2cur.execute(sqlCommand)
    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)
    finally:
        if (s2con):
            s2cur.close()
            s2con.close()
    for (s2os, s2osDef) in s2def.items():
        if not os.path.isfile('data/db/%s.db' % s2os):
            try:
                s2con = sqlite3.connect('data/db/%s.db' % s2os) 
                s2cur =  s2con.cursor()
                s2special = s2osDef['special'].split(sep=" ")
                for (s2param, defs) in s2osDef['options'].items():
                    for metric in defs['data']:
                        s2table = defs['alias'] + "." + metric["id"]
                        print("Creating table %s on database %s.db" % (s2table,s2os))
                        sqlCommand = '''CREATE TABLE "{}"("name" TEXT, "date" TEXT,'''.format(s2table)
                        if s2param in s2special:
                            sqlCommand = sqlCommand + " \"dev\" TEXT,"
                        for param in metric['parameter'].split(sep=" "):
                            if "%" in param:
                                param = param.split(sep="%")[1]
                            elif "/" in param:
                                param = param.split(sep="/")[0]
                            sqlCommand = sqlCommand + " \"" + param + "\" REAL,"
                        sqlCommand = sqlCommand[:-1] + ")"
                        s2cur.execute(sqlCommand)
            except sqlite3.Error as error:
                print("Error while connecting to sqlite", error)
            finally:
                if (s2con):
                    s2cur.close()
                    s2con.close()

def updateDb (s2filename, s2dir):
    s2tmp = s2dir + '/' + s2filename.split('.')[0]
    with tarfile.open(s2dir + '/' + s2filename) as tar:
        tar.extractall(path=s2tmp)
    for s2os in os.listdir(s2tmp + '/sar2html'):
        try:
            s2con = sqlite3.connect('data/db/%s.db' % s2os.lower())
            s2cur =  s2con.cursor()
            for s2host in os.listdir(s2tmp + '/sar2html/%s' % s2os):
                s2special = s2def[s2os.lower()]['special'].split(sep=" ")
                for (s2param, defs) in s2def[s2os.lower()]['options'].items():
                    for metric in defs['data']:
                        s2table = defs['alias'] + "." + metric["id"]
                        s2datafile = s2param + "." + metric["id"]
                        for s2file in os.listdir(s2tmp + '/sar2html/%s/%s/report' % (s2os,s2host)):
                            if s2file.startswith(s2datafile):
                                s2df = pd.read_csv(s2tmp + '/sar2html/%s/%s/report/%s' % (s2os,s2host,s2file), sep=" ", header=None)
                                s2dftime = s2df[0].str.replace('.','-',regex=True) + " " + s2df[1]
                                s2df[1] = s2dftime
                                s2df[0] = s2host
                                for column in s2df.loc[:,2:]:
                                    s2df[column] = s2df[column].astype(str)
                                    s2df[column] = s2df[column].str.replace(',','.',regex=True)
                                    s2df[column] = s2df[column].astype(float)
                                if s2param in s2special:
                                    s2dev = s2file.split(sep="--")[1]
                                    s2df.insert(2,'dev',s2dev,True)
                                sqlCommand = '''SELECT * FROM "{}"'''.format(s2table)
                                s2cur.execute(sqlCommand)
                                s2col = list(map(lambda x: x[0], s2cur.description))
                                s2df.columns = s2col
                                s2df.to_sql(s2table, s2con, if_exists = 'append', index = False)
                                if s2param in s2special:
                                    sqlCommand = 'DELETE FROM "{}" WHERE name = "{}" and rowid not in (SELECT min(rowid) FROM "{}" WHERE name = "{}" GROUP BY date, name, dev)'.format(s2table, s2host, s2table, s2host)
                                else:
                                    sqlCommand = 'DELETE FROM "{}" WHERE name = "{}" and rowid not in (SELECT min(rowid) FROM "{}" WHERE name = "{}" GROUP BY date, name)'.format(s2table, s2host, s2table, s2host)
                                s2con.execute(sqlCommand)
                                s2con.commit()
        except sqlite3.Error as error:
            print("Error while connecting to sqlite", error)
        finally:
            if (s2con):
                s2cur.close()
                s2con.close()

    for s2os in os.listdir(s2tmp + '/sar2html'):
        for s2host in os.listdir(s2tmp + '/sar2html/%s' % s2os):
            try:
                s2con = sqlite3.connect('data/db/hosts.db')
                s2cur =  s2con.cursor()
                sqlCommand = 'SELECT * from "hosts" where name = "{}"'.format(s2host)
                hostControl = s2cur.execute(sqlCommand)
                if len(hostControl.fetchall()) == 0:
                    sqlCommand = '''INSERT INTO "hosts" (name, os) VALUES("{}", "{}")'''.format(s2host, s2os.lower())
                    s2cur.execute(sqlCommand)
                    s2con.commit()
            except sqlite3.Error as error:
                print("Error while connecting to sqlite", error)
            finally:
                if (s2con):
                    s2cur.close()
                    s2con.close()

    shutil.rmtree(s2tmp)
    os.remove(s2dir + '/' + s2filename)
    return s2host

def deleteFromDb (hostId, range):
    host = get_host(hostId)
    s2os = host['os']
    s2host = host['name']
    if not range == 'all':
        range = range.split(';')
        range = [datetime.utcfromtimestamp(int(i)/1000).strftime('%Y-%m-%d %H:%M:%S') for i in range]
    else:
        range = []

    try:
        s2con = sqlite3.connect('data/db/%s.db' % s2os)
        s2cur =  s2con.cursor()
        for (s2param, defs) in s2def[s2os]['options'].items():
            for metric in defs['data']:
                s2table = defs['alias'] + "." + metric["id"]
                if range:
                    s2df = pd.read_sql_query('SELECT * FROM "{}" WHERE name = "{}"'.format(s2table, s2host), s2con)
                    s2df['date'] = pd.to_datetime(s2df['date'])
                    mask = (s2df['date'] < range[0]) | (s2df['date'] > range[1])
                    s2df = s2df.loc[mask]
                sqlCommand = '''DELETE FROM "{}" WHERE name = "{}"'''.format(s2table, s2host)
                s2cur.execute(sqlCommand)
                s2con.commit()
                if range:
                    if not s2df.empty:
                        s2df.to_sql(s2table, s2con, if_exists = 'append', index = False)
        s2df = pd.read_sql_query('SELECT * FROM "{}" WHERE name = "{}"'.format(s2def[s2os]['options']['b']['alias'] + '.1', s2host), s2con)
    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)
    finally:
        if (s2con):
            s2cur.close()
            s2con.close()

    try:
        s2con = get_db_connection('hosts.db')
        if s2df.empty:
            s2con.execute('DELETE FROM hosts WHERE id = ?', (hostId,))
            s2con.commit()
    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)
    finally:
        if (s2con):
            s2con.close()
    
    if range:
        flash('Data from "{}" to "{}" of host "{}" was successfully deleted!'.format(range[0], range[1], s2host))
    else:
        flash('"{}" was successfully deleted!'.format(s2host))

    if s2df.empty:
        return True
    else:
        return False


def getPlot(source, dev, init, title):
    label = alt.selection(type='single', nearest=True, on='mouseover',
                            fields=['date'], empty='none')

    selection = alt.selection_multi(fields=['variable'], bind='legend')
    brush = alt.selection(type='interval', encodings=['x'])
    if dev:
        selectBox = alt.binding_select(options=list(source['dev'].unique()), name="Device ")
        drop = alt.selection_single(name='Select', fields=['dev'], bind=selectBox, init={'dev': init})
        base = alt.Chart(source, title='{}'.format(title)).mark_line(interpolate='basis').encode(
            x = 'date:T',
            y = 'value:Q',
            color='variable:N',
            opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
        ).transform_filter(
            drop
        )
        myplot = alt.layer(
            base, # base line chart
    
            # add a rule mark to serve as a guide line
            alt.Chart().mark_rule(color='#aaa').encode(
                x='date:T'
            ).transform_filter(label),
    
            # add circle marks for selected time points, hide unselected points
            base.mark_circle().encode(
                opacity=alt.condition(label, alt.value(1), alt.value(0))
            ).add_selection(label),
    
            # add white stroked text to provide a legible background for labels
            base.mark_text(align='left', dx=5, dy=-5, stroke='white', strokeWidth=4).encode(
                text='value:Q'
            ).transform_filter(label),
    
            # add text labels for stock prices
            base.mark_text(align='left', dx=5, dy=-5).encode(
                text='value:Q'
            ).transform_filter(label)
        ).add_selection(
            selection, drop
        ).properties(
            width=800,
            height=300,
            description="{}".format(title)
        )
    else:
        base = alt.Chart(source, title=title).mark_line(interpolate='basis').encode(
            x='date:T',
            y='value:Q',
            color='variable:N',
            opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
        )
        myplot = alt.layer(
            base, # base line chart

            # add a rule mark to serve as a guide line
            alt.Chart().mark_rule(color='#aaa').encode(
                x='date:T'
            ).transform_filter(label),

            # add circle marks for selected time points, hide unselected points
            base.mark_circle().encode(
                opacity=alt.condition(label, alt.value(1), alt.value(0))
            ).add_selection(label),

            # add white stroked text to provide a legible background for labels
            base.mark_text(align='left', dx=5, dy=-5, stroke='white', strokeWidth=4).encode(
                text='value:Q'
            ).transform_filter(label),

            # add text labels for stock prices
            base.mark_text(align='left', dx=5, dy=-5).encode(
                text='value:Q'
            ).transform_filter(label)
        ).add_selection(
            selection
        ).properties(
            width=800,
            height=300,
            description="{}".format(title)
        )
    return myplot

def get_db_connection(dbName):
    conn = sqlite3.connect('data/db/' + dbName)
    conn.row_factory = sqlite3.Row
    return conn

def get_host(host_id):
    conn = get_db_connection('hosts.db')
    host = conn.execute('SELECT * FROM hosts WHERE id = ?',
                        (host_id,)).fetchone()
    conn.close()
    if host is None:
        abort(404)
    return host

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['UPLOAD_EXTENSIONS']

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'data/tmp'
app.config['UPLOAD_EXTENSIONS'] = ['.tar', '.gz', '.tar.gz']
app.config['DROPZONE_UPLOAD_MULTIPLE'] = True
app.config['SECRET_KEY'] = 'sar209@dnmduf8!23jQa'
alt.renderers.enable('default')
alt.data_transformers.enable('data_server')

try:
    data_file = open('conf/sar2def.json')
    s2def = json.load(data_file)
    data_file.close()
except:
    print('sar2def.json definition file does not exist!')
    exit(1)

if not os.path.isdir('data'):
    os.mkdir('data')
if not os.path.isdir('data/db'):
    os.mkdir('data/db')
if not os.path.isdir('data/tmp'):
    os.mkdir('data/tmp')
if not os.path.isfile('data/db/hosts.db'):
    initializeDb()

@app.route('/')
def index():
    #print(request.form)
    conn = get_db_connection('hosts.db')
    hosts = conn.execute('SELECT * FROM hosts ORDER by name').fetchall()
    conn.close()
    return render_template('index.html', hosts=hosts)
    
@app.route('/', methods=['POST'])
def upload_files():
    hostList = []
    uploadedFiles = request.files.getlist("file")
    for uploadedFile in uploadedFiles:
        fileName = secure_filename(uploadedFile.filename)
        if fileName != '':
            fileExt = os.path.splitext(fileName)[1]
            if fileExt in app.config['UPLOAD_EXTENSIONS']:
                uploadedFile.save(os.path.join(app.config['UPLOAD_FOLDER'], fileName))
                host = updateDb(fileName, app.config['UPLOAD_FOLDER'])
                hostList.append(host)
        
    if len(hostList) > 1:
        flash('"{}" were successfully added!'.format(', '.join(hostList)))
    else:
        flash('"{}" was successfully added!'.format(', '.join(hostList)))
    return redirect(url_for('index'))
    
@app.route('/<int:host_id>', methods=('GET', 'POST'))
def post(host_id):
    host = get_host(host_id)
    s2os = host['os']
    s2host = host['name']
    conn = sqlite3.connect('data/db/' + s2os + '.db')
    df = pd.read_sql_query('SELECT * FROM "{}" WHERE name = "{}"'.format(s2def[s2os]['options']['b']['alias'] + '.1', host['name']), conn)
    df['date'] = pd.to_datetime(df['date'])
    datedf = df['date'].dt.date.drop_duplicates()
    datedf = pd.DataFrame({'date':datedf.values})
    datedf = datedf.sort_values(by="date")
    datedf['date'] = pd.to_datetime(datedf['date'])
    datedf['date'] = (datedf['date'] - datetime(1970,1,1)).dt.total_seconds() * 1000
    values = datedf['date'].tolist()
    values = list(map(int, values))
    startDate = values[-1]
    endDate = startDate + 86400000
    values.append(endDate)
    if request.method == 'POST':
        dateRange = request.form['dateSlider']
        dateRange = dateRange.split(';')
        startDate = dateRange[0]
        endDate = dateRange[1]
    
    sDate = int(int(startDate)/1000)
    sDate = datetime.utcfromtimestamp(sDate).strftime('%Y-%m-%d %H:%M:%S')
    eDate = int(int(endDate)/1000)
    eDate = datetime.utcfromtimestamp(eDate).strftime('%Y-%m-%d %H:%M:%S')

    charts = []
    titles = []
    s2init = "" 
    s2special = s2def[s2os]['special'].split(sep=" ")
    for (s2param, s2defs) in s2def[s2os]['options'].items():
        for s2metric in s2defs['data']:
            s2table = s2defs['alias'] + "." + s2metric["id"]
            s2par = s2metric["parameter"].replace('/s', '').replace('%', '').split(' ')
            s2title = s2metric["title"]
            s2df = pd.read_sql_query('SELECT * FROM "{}" where name="{}"'.format(s2table, s2host), conn)
            if not s2df.empty:
                if not s2defs['title'] in titles:
                    titles.append(s2defs['title'])
                else:
                    titles.append('')
                s2df['date'] = pd.to_datetime(s2df['date'])

                if s2param in s2special:
                    s2df = s2df.sort_values(["dev", "date"])
                    s2df = pd.melt(s2df, id_vars =['name','date', 'dev'], value_vars = s2par)
                    s2init = s2df.sort_values('dev')['dev'].unique()[0]
                    s2dev = True
                else:
                    s2df = pd.melt(s2df, id_vars =['name','date'], value_vars = s2par)
                    s2dev = False
    
                mask = (s2df['date'] > sDate) & (s2df['date'] <= eDate)
                s2df = s2df.loc[mask]
                chart = getPlot(s2df, s2dev, s2init, s2title)
                chart = chart.to_json().replace("\n", "").replace("\t","")
                charts.append(chart)
    
    conn.close()
    return render_template('post.html', host=host, values=values, start=startDate, end=endDate, charts=charts, titles=titles)


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print('hey')
        return redirect(url_for('index'))
    else:
        return render_template('create.html')


@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_host(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)


@app.route('/<int:host_id>/delete', methods=['POST'])
def delete(host_id):
    dateRange = request.form['dateSlider']
    delete = deleteFromDb(host_id, dateRange)
    if delete:
        return redirect(url_for('index'))
    else:
        return redirect(url_for('post', host_id=host_id))

if __name__ == '__main__':
    app.run(debug=True)

