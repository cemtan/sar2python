import argparse
import sqlite3 
import json
import os
import sys
import tarfile
import pandas
import shutil

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, 'r')  # return an open file handle

def initialize_s2():
    if not os.path.isdir('sarDATA'):
        os.mkdir('sarDATA')
    if not os.path.isdir('sarDATA/db'):
        os.mkdir('sarDATA/db')
    if not os.path.isdir('sarDATA/tmp'):
        os.mkdir('sarDATA/tmp')
    for (s2os, s2os_def) in s2def.items():
        if not os.path.isfile('sarDATA/db/%s.db' % s2os):
            try:
                s2con = sqlite3.connect('sarDATA/db/%s.db' % s2os) 
                s2cur =  s2con.cursor()
                s2special = s2os_def['special'].split(sep=" ")
                for (s2param, defs) in s2os_def['options'].items():
                    for metric in defs['data']:
                        s2table = defs['alias'] + "." + metric["id"]
                        print("Creating table %s on database %s.db" % (s2table,s2os))
                        sql_command = '''CREATE TABLE "{}"("name" TEXT, "date" TEXT,'''.format(s2table)
                        if s2param in s2special:
                            sql_command = sql_command + " \"dev\" TEXT,"
                        for param in metric['parameter'].split(sep=" "):
                            if "%" in param:
                                param = param.split(sep="%")[1]
                            elif "/" in param:
                                param = param.split(sep="/")[0]
                            sql_command = sql_command + " \"" + param + "\" REAL,"
                        sql_command = sql_command[:-1] + ")"
                        s2cur.execute(sql_command)
            except sqlite3.Error as error:
                print("Error while connecting to sqlite", error)
            finally:
                if (s2con):
                    s2cur.close()
                    s2con.close()

def merge_s2(s2files):
    for s2file in s2files:
        with tarfile.open('%s' % s2file.name) as tar:
            tar.extractall(path='sarDATA/tmp')
    for s2os in os.listdir('sarDATA/tmp/sar2html'):
        for s2host in os.listdir('sarDATA/tmp/sar2html/%s' % s2os):
            s2special = s2def[s2os.lower()]['special'].split(sep=" ")
            for (s2param, defs) in s2def[s2os.lower()]['options'].items():
                for metric in defs['data']:
                    s2table = defs['alias'] + "." + metric["id"]
                    s2datafile = s2param + "." + metric["id"]
                    for s2file in os.listdir('sarDATA/tmp/sar2html/%s/%s/report' % (s2os,s2host)):
                        if s2file.startswith(s2datafile):
                            s2df = pandas.read_csv('sarDATA/tmp/sar2html/%s/%s/report/%s' % (s2os,s2host,s2file), sep=" ", header=None)
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
                            try: 
                                s2con = sqlite3.connect('sarDATA/db/%s.db' % s2os.lower()) 
                                s2cur =  s2con.cursor()
                                sql_command = '''SELECT * FROM "{}"'''.format(s2table)
                                s2cur.execute(sql_command)
                                s2col = list(map(lambda x: x[0], s2cur.description))
                                s2df.columns = s2col
                                s2df.to_sql(s2table, s2con, if_exists = 'append', index = False)
                            except sqlite3.Error as error:
                                print("Error while connecting to sqlite", error)
                            finally:
                                if (s2con):
                                    s2cur.close()
                                    s2con.close()
    shutil.rmtree('sarDATA/tmp/sar2html')
            



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--initialize", action="store_true", help="Initialize sar2html")
    parser.add_argument("-l", "--list", choices=['single', 'all'], help="List the tenants if at least one or all ASM(s) logged in")
    parser.add_argument("-r", "--report", action="store_true", help="Generate complete report")
    parser.add_argument("-m", "--merge", dest="s2report", nargs='+', help="Only extract and merge new data", type=lambda x: is_valid_file(parser, x))
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    try:
        data_file = open('sarFILE/config/sar2def.json')
        s2def = json.load(data_file)
        data_file.close()
    except:
        print('sar2def.json definition file does noe exist!')
        exit(1)

    if args.initialize:
        initialize_s2()

    if args.s2report:
        merge_s2(args.s2report)

