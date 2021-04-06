import sqlite3 
import json
import os

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

s2os = os.listdir("/tmp/sar2html")[0]
if not s2os.lower() in s2def:
    print("OS type is not supported!")
    exit(1)

s2host = os.listdir("/tmp/sar2html/%s" % s2os)[0]
s2files = os.listdir("/tmp/sar2html/%s/%s/report" % (s2os,s2host))
s2path = "/tmp/sar2html/" + s2os + "/" + s2host + "/report/" 

for s2file in s2files:
    if len(s2file.split(sep="--")):
        dev = "none"
        s2fileopt = s2file
    else:
        dev = s2file.split(sep="--")[1]
        s2fileopt = s2file.split(sep="--")[0]
    s2param = s2fileopt.split(sep=".")[0]
    s2id = s2fileopt.split(sep=".")[1]
    parameter = s2def[s2os.lower()]['options'][s2param]['data'][int(s2id)]['parameter'].split(sep=" "):
    with open(s2path + s2file, "r") as s2data:
        for line in s2data:
            stripped_line = line.strip()
    
