import sqlite3 
import json

def table_exists(table_name): 
    s2cur.execute('''SELECT count(name) FROM sqlite_master WHERE TYPE = 'table' AND name = '{}' '''.format(table_name)) 
    if s2cur.fetchone()[0] == 1: 
        return True 
    return False

s2con = sqlite3.connect('sarDATA/sar2html.db') 
s2cur =  s2con.cursor()

try:
    data_file = open('sarFILE/config/sar2def.json')
    s2def = json.load(data_file)
    data_file.close()
except:
    print('sar2def.json definition file does noe exist!')
    exit(1)

for (s2os, s2os_def) in s2def.items():
    if not table_exists(s2os):
        print("Creating table %s on database sar2html.db" % s2os)
        sql_command = '''CREATE TABLE "{}"("name" TEXT, "date" TEXT, "time" TEXT, "dev" TEXT,'''.format(s2os)

        for (s2param, metrics) in s2os_def['options'].items():
            for metric in metrics['data']:
                for param in metric['parameter'].split(sep=" "):
                    if "%" in param:
                        param = param.split(sep="%")[1]
                    elif "/" in param:
                        param = param.split(sep="/")[0]
                    sql_command = sql_command + " \"" + s2param + "." + metric["id"] + "." + param + "\" REAL,"
        
        sql_command = sql_command[:-1] + ")"
        s2cur.execute(sql_command)
