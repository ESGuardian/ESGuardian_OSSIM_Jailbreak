#! /usr/bin/python
# -*- coding: cp1251 -*-
# ����� esguardian@outlook.com
# ������ 1.0.1
# ����� �� ��������� ���������� �� ������� �������� � �������� 
# �������� �� ���� ������ ������� OSSEC � �������� ��������� Windows/Unix ����������
# � ����� ������ ����������� "�������������" �������� (skype, torrent � �.�.)
# ��� ����������� ������ ����� ���� ����� OSSEC � ������� ������� � �������� 
#
import sys
import MySQLdb
import codecs
from datetime import date, timedelta
from OSSIM_helper import get_db_connection_data


# Datababe connection config.
(dbhost,dbuser,dbpass) = get_db_connection_data()
dbschema='alienvault_siem'
# --- End of Database config

# ---- Init 

period=1
if len(sys.argv) > 1:
    period=int(sys.argv[1])


today=date.today()
enddate=today.strftime('%Y:%m:%d')
endtime=enddate + ' 06:00:00' # UTC time
startdate=(today - timedelta(days=period)).strftime('%Y:%m:%d')
starttime=startdate + ' 06:00:00'
when = "timestamp between '" + starttime + "' and '" + endtime + "'"
outfilename='APP-' + today.strftime('%Y-%m-%d') + '.csv'
outfullpath='/usr/local/ossim_reports/' + outfilename

mytz="'+03:00'"
mycharset='cp1251'
dbcharset='utf8'
colheader='��������;�����;���������;������\n'.decode(mycharset)


conn = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpass, db=dbschema, charset='utf8') 
cursor = conn.cursor() 

# ---- End of Init

# Windows app monitor
tabheader='\n\n���������� �������� Windows �� ������ '.decode(mycharset) + startdate + ' - ' + enddate + '\n\n'
what = "convert_tz(timestamp,'+00:00'," + mytz +") as time, inet_ntoa(conv(HEX(ip_src), 16, 10)), substring_index(substring_index(data_payload,'[INIT]',-1),'[END]',1) from acid_event join extra_data on (id=event_id)"
where = "acid_event.plugin_id=7093 and acid_event.plugin_sid=514"
select="select " + what + " where "  + where + " and " + when + " order by time"
cursor.execute(select)
with codecs.open(outfullpath, 'a', encoding=mycharset) as out:
     out.write(tabheader + colheader) 
     row = cursor.fetchone() 
     while row:
         out.write('Windows application monitor event;' + ';'.join([str(c).decode(dbcharset).replace(';',',') for c in row]) + '\n')
         row = cursor.fetchone()
out.close()
# ---
# Windows APP install/uninstall
tabheader = '\n\n��������� �������� Windows �� ������ '.decode(mycharset) + startdate + ' - ' + enddate + '\n\n'
what = "userdata3 as action, convert_tz(timestamp,'+00:00'," + mytz +") as time, inet_ntoa(conv(HEX(ip_src), 16, 10)) as source, concat('MsiInstaller: ',substring_index(substring_index(substring_index(data_payload,'MsiInstaller: ',-1),'[END]',1),' (NULL)',1)) as info from acid_event join extra_data on id=event_id"
where = "acid_event.plugin_id=7006 and (acid_event.plugin_sid=18147 or acid_event.plugin_sid=18146)"
select="select " + what + " where "  + where + " and " + when + " order by time"
cursor.execute(select)
with codecs.open(outfullpath, 'a', encoding=mycharset) as out:
     out.write(tabheader + colheader) 
     row = cursor.fetchone() 
     while row:
         out.write(';'.join([str(c).decode(dbcharset).replace(';',',') for c in row]) + '\n')
         row = cursor.fetchone()
out.close()
# ---
# Linux package install
tabheader='\n\n��������� ������� Linux �� ������ '.decode(mycharset) + startdate + ' - ' + enddate + '\n\n'
what = "convert_tz(timestamp,'+00:00'," + mytz +") as time, inet_ntoa(conv(HEX(ip_src), 16, 10)), substring_index(substring_index(data_payload,'[INIT]',-1),'[END]',1) from acid_event join extra_data on id=event_id"
where = "acid_event.plugin_id=7042 and acid_event.plugin_sid=2902"
select="select " + what + " where "  + where + " and " + when + " order by time"
cursor.execute(select)
with codecs.open(outfullpath, 'a', encoding=mycharset) as out:
     out.write(tabheader + colheader) 
     row = cursor.fetchone() 
     while row:
         out.write('Linux Package installed;' + ';'.join([str(c).decode(dbcharset).replace(';',',') for c in row]) + '\n')
         row = cursor.fetchone()
out.close()
# ---
#  Integrity checksum changed.
tabheader='\n\n��������� ����������� ���� ������ �� ������ '.decode(mycharset) + startdate + ' - ' + enddate + '\n\n'
what = "convert_tz(timestamp,'+00:00'," + mytz +") as time, inet_ntoa(conv(HEX(ip_src), 16, 10)), substring_index(substring_index(data_payload,'[INIT]Integrity checksum changed for: ''',-1),'''',1) from acid_event join extra_data on id=event_id"
where = "acid_event.plugin_id=7094 and (acid_event.plugin_sid=550 or acid_event.plugin_sid=551 or acid_event.plugin_sid=552)"
select="select " + what + " where "  + where + " and " + when + " order by time"
cursor.execute(select)
with codecs.open(outfullpath, 'a', encoding=mycharset) as out:
     out.write(tabheader + colheader) 
     row = cursor.fetchone() 
     while row:
         out.write('Integrity checksum changed.;' + ';'.join([str(c).decode(dbcharset).replace(';',',') for c in row]) + '\n')
         row = cursor.fetchone()
out.close()
# ---
# --- End of All
conn.close()
