import sqlite3 
import json

def table_exists(table_name): 
    s2cur.execute('''SELECT count(name) FROM sqlite_master WHERE TYPE = 'table' AND name = '"{}"' '''.format(table_name)) 
    if s2cur.fetchone()[0] == 1: 
        return True 
    return False

try:
    data_file = open('sarFILE/config/sar2def.json')
    s2def = json.load(data_file)
    data_file.close()
except:
    print('sar2def.json definition file does noe exist!')
    exit(1)

for (s2os, s2os_def) in s2def.items():
    try:
        s2con = sqlite3.connect('sarDATA/%s.db' % s2os) 
        s2cur =  s2con.cursor()
        s2special = s2os_def['special'].split(sep=" ")
        for (s2param, s2defs) in s2os_def['options'].items():
            for metric in s2defs['data']:
                s2table = s2defs['alias'] + "." + metric["id"]
                if not table_exists(s2table):
                    print("Creating table %s on database %s.db" % (s2table,s2os))
                    sql_command = '''CREATE TABLE "{}"("name" TEXT, "date" TEXT, "time" TEXT,'''.format(s2table)
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
