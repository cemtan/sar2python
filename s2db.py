import sqlite3 
import json

def table_exists(table_name): 
    s2cur.execute('''SELECT count(name) FROM sqlite_master WHERE TYPE = 'table' AND name = '{}' '''.format(table_name)) 
    if s2cur.fetchone()[0] == 1: 
        return True 
    return False

def get_data(): 
    s2cur.execute('''SELECT * FROM redhat_5''') 
    data = [] 
    for row in s2cur.fetchall(): 
        data.append(row) 
    return data

s2con = sqlite3.connect('sarDATA/sar2html.db') 
s2cur =  s2con.cursor()



if not table_exists('redhat_3'):
    print("Creating table redhat_3 on database sar2html.db")
    s2cur.execute('''
        CREATE TABLE redhat_3(
            "name" TEXT,
            "date" TEXT,
            "time" TEXT,
            "dev" TEXT,
            "b.1_tps" REAL,
            "b.1_rtps" REAL,
            "b.1_wtps" REAL,
            "b.2_bread" REAL,
            "b.2_bwrtn" REAL,
            "B.1_pgpgin" REAL,
            "B.1_pgpgout" REAL,
            "B.2_fault" REAL,
            "B.2_majflt" REAL,
            "c.1_proc" REAL,
            "d.1_tps" REAL,
            "d.2_rd_sec" REAL,
            "d.2_wr_sec" REAL,
            "I_SUM.1_intr" REAL,
            "n_DEV.1_rxbyt" REAL,
            "n_DEV.1_txbyt" REAL,
            "n_DEV.2_rxpck" REAL,
            "n_DEV.2_txpck" REAL,
            "n_DEV.2_rxcmp" REAL,
            "n_DEV.2_txcmp" REAL,
            "n_DEV.2_rxmcst" REAL,
            "n_EDEV.1_rxerr" REAL,
            "n_EDEV.1_txerr" REAL,
            "n_EDEV.1_coll" REAL,
            "n_EDEV.1_rxdrop" REAL,
            "n_EDEV.1_txdrop" REAL,
            "n_EDEV.1_txcarr" REAL,
            "n_EDEV.1_rxfram" REAL,
            "n_EDEV.1_rxfifo" REAL,
            "n_EDEV.1_txfifo" REAL,
            "n_SOCK.1_totsck" REAL,
            "n_SOCK.1_tcpsck" REAL,
            "n_SOCK.1_udpsck" REAL,
            "n_SOCK.1_rawsck" REAL,
            "n_SOCK.1_ip-frag" REAL,
            "P_ALL.1_user" REAL,
            "P_ALL.1_nice" REAL,
            "P_ALL.1_system" REAL,
            "P_ALL.1_iowait" REAL,
            "P_ALL.1_idle" REAL,
            "q.1_runq-sz" REAL,
            "q.2_plist-sz" REAL,
            "q.3_ldavg-1" REAL,
            "q.3_ldavg-5" REAL,
            "q.3_ldavg-15" REAL,
            "r.1_kbmemfree" REAL,
            "r.1_kbmemused" REAL,
            "r.1_kbbuffers" REAL,
            "r.1_kbcached" REAL,
            "r.2_kbswpfree" REAL,
            "r.2_kbswpused" REAL,
            "r.2_kbswpcad" REAL,
            "r.3_memused" REAL,
            "r.3_swpused" REAL,
            "R.1_frmpg" REAL,
            "R.1_bufpg" REAL,
            "R.1_campg" REAL,
            "v.1_dentunusd" REAL,
            "v.2_file-sz" REAL,
            "v.3_inode-sz" REAL,
            "v.4_super-sz" REAL,
            "v.5_dquot-sz" REAL,
            "v.6_rtsig-sz" REAL,
            "v.7_super-sz" REAL,
            "v.7_dquot-sz" REAL,
            "v.7_rtsig-sz" REAL,
            "w.1_cswch" REAL,
            "W.1_pswpin" REAL,
            "W.1_pswpout" REAL,
            "y.1_rcvin" REAL,
            "y.1_xmtin" REAL
        )
    ''')

if not table_exists('redhat_5'):
    print("Creating table redhat_5 on database sar2html.db")
    s2cur.execute('''
        CREATE TABLE redhat_5(
            "name" TEXT,
            "date" TEXT,
            "time" TEXT,
            "dev" TEXT,
            "b.1_tps" REAL,
            "b.1_rtps" REAL,
            "b.1_wtps" REAL,
            "b.2_bread" REAL,
            "b.2_bwrtn" REAL,
            "B.1_pgpgin" REAL,
            "B.1_pgpgout" REAL,
            "B.2_fault" REAL,
            "B.2_majflt" REAL,
            "c.1_proc" REAL,
            "d.1_tps" REAL,
            "d.2_rd_sec" REAL,
            "d.2_wr_sec" REAL,
            "d.3_avgrq-sz" REAL,
            "d.3_avgqu-sz" REAL,
            "d.4_await" REAL,
            "d.5_svctm" REAL,
            "d.6_util" REAL,
            "I_SUM.1_intr" REAL,
            "n_DEV.1_rxbyt" REAL,
            "n_DEV.1_txbyt" REAL,
            "n_DEV.2_rxpck" REAL,
            "n_DEV.2_txpck" REAL,
            "n_DEV.2_rxcmp" REAL,
            "n_DEV.2_txcmp" REAL,
            "n_DEV.2_rxmcst" REAL,
            "n_EDEV.1_rxerr" REAL,
            "n_EDEV.1_txerr" REAL,
            "n_EDEV.1_coll" REAL,
            "n_EDEV.1_rxdrop" REAL,
            "n_EDEV.1_txdrop" REAL,
            "n_EDEV.1_txcarr" REAL,
            "n_EDEV.1_rxfram" REAL,
            "n_EDEV.1_rxfifo" REAL,
            "n_EDEV.1_txfifo" REAL,
            "n_NFS.1_read" REAL,
            "n_NFS.1_write" REAL,
            "n_NFS.2_call" REAL,
            "n_NFS.2_retrans" REAL,
            "n_NFS.2_access" REAL,
            "n_NFS.2_getatt" REAL,
            "n_NFSD.1_sread" REAL,
            "n_NFSD.1_swrite" REAL,
            "n_NFSD.2_scall" REAL,
            "n_NFSD.2_badcall" REAL,
            "n_NFSD.2_saccess" REAL,
            "n_NFSD.2_sgetatt" REAL,
            "n_NFSD.3_packet" REAL,
            "n_NFSD.3_udp" REAL,
            "n_NFSD.3_tcp" REAL,
            "n_NFSD.4_hit" REAL,
            "n_NFSD.4_miss" REAL,
            "n_SOCK.1_totsck" REAL,
            "n_SOCK.1_tcpsck" REAL,
            "n_SOCK.1_udpsck" REAL,
            "n_SOCK.1_rawsck" REAL,
            "n_SOCK.1_ip-frag" REAL,
            "P_ALL.1_user" REAL,
            "P_ALL.1_nice" REAL,
            "P_ALL.1_system" REAL,
            "P_ALL.1_iowait" REAL,
            "P_ALL.1_steal" REAL,
            "P_ALL.1_idle" REAL,
            "q.1_runq-sz" REAL,
            "q.2_plist-sz" REAL,
            "q.3_ldavg-1" REAL,
            "q.3_ldavg-5" REAL,
            "q.3_ldavg-15" REAL,
            "r.1_kbmemfree" REAL,
            "r.1_kbmemused" REAL,
            "r.1_kbbuffers" REAL,
            "r.1_kbcached" REAL,
            "r.2_kbswpfree" REAL,
            "r.2_kbswpused" REAL,
            "r.2_kbswpcad" REAL,
            "r.3_memused" REAL,
            "r.3_swpused" REAL,
            "R.1_frmpg" REAL,
            "R.1_bufpg" REAL,
            "R.1_campg" REAL,
            "v.1_dentunusd" REAL,
            "v.2_file-sz" REAL,
            "v.3_inode-sz" REAL,
            "v.4_super-sz" REAL,
            "v.5_dquot-sz" REAL,
            "v.6_rtsig-sz" REAL,
            "v.7_super-sz" REAL,
            "v.7_dquot-sz" REAL,
            "v.7_rtsig-sz" REAL,
            "w.1_cswch" REAL,
            "W.1_pswpin" REAL,
            "W.1_pswpout" REAL,
            "y.1_rcvin" REAL,
            "y.1_xmtin" REAL,
            "y.1_framerr" REAL,
            "y.1_prtyerr" REAL,
            "y.1_brk" REAL,
            "y.1_ovrun" REAL
        )
    ''')

#s2cur.execute("PRAGMA table_info(redhat_5)")
#print(s2cur.fetchall())

#print(get_data())

try:
    data_file = open('sarFILE/config/sar2def.json')
    s2def = json.load(data_file)
    data_file.close()
except:
    print('sar2def.json definition file does noe exist!')
    exit(1)

for (k, v) in s2def['redhat_3']['options'].items():
    print("Key: " + k)
    print("Value: " + str(v))