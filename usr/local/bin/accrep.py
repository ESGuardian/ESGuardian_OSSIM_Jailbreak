#! /usr/bin/python
# -*- coding: cp1251 -*-
# ����� esguardian@outlook.com
# ������ 1.0.4
# ----------
# 09.09.2015. ��������� ������ �� payload ���������� �� SQL ������� � ���� �������
# ��� ������� ��������
# -----------------------
# ����� � ��������� � �������� �������� 
# �������� �� ���� ������ ������� OSSEC � ����������/�������� ������������� � ������
# ��������/��������/����������/������������� ������� �������
# ��������/�������� �����
# ��� ����������� ������ ����� ���� ����� OSSEC � ������������ ������� 
# � (����������) � ������� �������  
#
import sys
import string
import MySQLdb
import codecs
from datetime import date, timedelta
from OSSIM_helper import get_db_connection_data


# Datababe connection config.
(dbhost,dbuser,dbpass) = get_db_connection_data()
dbshema='alienvault_siem'
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

outfilename='AC-' + today.strftime('%Y-%m-%d') + '.csv'
outfullpath='/usr/local/ossim_reports/' + outfilename

mytz="'+03:00'"
mycharset='cp1251'
colheader=u'��������;�����;��������;������;���������;������\n'


conn = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpass, db=dbshema, charset='utf8') 
cursor = conn.cursor() 

# ---- End of Init
when = "timestamp between '" + starttime + "' and '" + endtime + "'"

# Account change
tabheader=u'\n\n\n��������� ������� ������� �� ������ ' + startdate + ' - ' + enddate + '\n\n'
what = "userdata3 as action, convert_tz(timestamp,'+00:00'," + mytz +") as time, userdata8 as operator, username as object, inet_ntoa(conv(HEX(ip_src), 16, 10)) as source, data_payload as info from acid_event join extra_data on (acid_event.id=extra_data.event_id)"
where = "acid_event.plugin_id=7043 and (acid_event.plugin_sid=18110 or acid_event.plugin_sid=18112 or acid_event.plugin_sid=18142)"
select = "select  " + what + " where " + where + " and " + when + " order by time"
cursor.execute(select)
with codecs.open(outfullpath, 'a', encoding=mycharset) as out:
    out.write(tabheader + colheader) 
    row = cursor.fetchone() 
    while row:
        outstr = row[0].replace(';',',').strip()
        outstr = outstr + ';' + str(row[1]).replace(';',',').strip()
        outstr = outstr + ';' + row[2].replace(';',',').strip()
        outstr = outstr + ';' + row[3].replace(';',',').strip()
        outstr = outstr + ';' + row[4].replace(';',',').strip()
        # ��������� �� payload ������ � ��������� ��������
        try:
            info = row[5].split('.inbank.msk: ', 1)[-1].split('Subject:',1)[0]
        except:
            info = row[5]
        outstr = outstr + ';' + info.replace(';',',').strip()
        out.write(outstr + '\n')
        row = cursor.fetchone()
out.close()
# ---
# global and universal group change
tabheader=u'\n\n\n��������� ���������� ����� �� ������ ' + startdate + ' - ' + enddate + '\n\n'

with codecs.open(outfullpath, 'a', encoding=mycharset) as out:
    out.write(tabheader + colheader) 
    # global group create
    what = "userdata3 as action, convert_tz(timestamp,'+00:00'," + mytz +") as time, username as operator, inet_ntoa(conv(HEX(ip_src), 16, 10)) as source, data_payload as info from acid_event join extra_data on (acid_event.id=extra_data.event_id)"
    where = "acid_event.plugin_id=7099 and acid_event.plugin_sid=18202"
    select = "select " + what + " where " + where + " and " + when  + " order by time"
    cursor.execute(select)
    row = cursor.fetchone() 
    while row:
        outstr = row[0].replace(';',',').strip()
        outstr = outstr + ';' + str(row[1]).replace(';',',').strip()
        outstr = outstr + ';' + row[2].replace(';',',').strip()
        # ��������� �������� ������ �� payload
        try:
            object = row[4].split('Group Name: ',1)[-1].split('Group',1)[0]
        except:
            object = 'None'
        outstr = outstr + ';' + object.replace(';',',').strip()
        outstr = outstr + ';' + row[3].replace(';',',').strip()
        # ��������� �������� �������� �� payload, ���� �� ��������� ������� payload ��� ����
        try:
            info = row[4].split('.inbank.msk: ', 1)[-1].split('Subject:',1)[0]
        except:
            info = row[4]
        outstr = outstr + ';' + info.replace(';',',').strip()
        out.write(outstr + '\n')
        row = cursor.fetchone()
        
    # global group member add or remove and universal group member remove
    what = "userdata3 as action, convert_tz(timestamp,'+00:00'," + mytz +") as time, username as operator, inet_ntoa(conv(HEX(ip_src), 16, 10)) as source, data_payload as info from acid_event join extra_data on (acid_event.id=extra_data.event_id)"
    where = "acid_event.plugin_id=7107 and (acid_event.plugin_sid=18203 or acid_event.plugin_sid=18204 or acid_event.plugin_sid=18215)"
    select = "select " + what + " where " + where + " and " + when  + " order by time"
    cursor.execute(select)
    row = cursor.fetchone() 
    while row:
        outstr = row[0].replace(';',',').strip()
        outstr = outstr + ';' + str(row[1]).replace(';',',').strip()
        outstr = outstr + ';' + row[2].replace(';',',').strip()
        # ��������� �������� ������ �� payload
        try:
            object = row[4].split('Group Name: ',1)[-1].split('Group',1)[0]
        except:
            object = 'None'
        outstr = outstr + ';' + object.replace(';',',').strip()
        outstr = outstr + ';' + row[3].replace(';',',').strip()
        # ��������� ��� ������������ �� payload, ���� �� ��������� ������� payload ��� ����
        try:
            info = string.capwords(row[4].lower().split('cn=', 1)[-1].split(',ou=',1)[0])
        except:
            info = row[4]
        outstr = outstr + ';' + info.replace(';',',').strip()
        out.write(outstr + '\n')
        row = cursor.fetchone()
    # Universal group member add 
    # Ooops, ossim save this record in other format than "member removed" I think this is ossec agent bug
    # so I need to do additional select
    what = "userdata3 as action, convert_tz(timestamp,'+00:00'," + mytz +") as time, inet_ntoa(conv(HEX(ip_src), 16, 10)) as source, data_payload as info from acid_event join extra_data on (acid_event.id=extra_data.event_id)"
    where = "acid_event.plugin_id=7107 and acid_event.plugin_sid=18214"
    select = "select " + what + " where " + where + " and " + when  + " order by time"
    cursor.execute(select)
    row = cursor.fetchone() 
    while row:
        outstr = row[0].replace(';',',').strip()
        outstr = outstr + ';' + str(row[1]).replace(';',',').strip()
        try:
            operator = row[3].split('Group: Security ID:',1)[-1].split(' Account Domain:',1)[0].split('Account Name: ')[-1]
        except:
            operator = 'None'
        outstr = outstr + ';' + operator.replace(';',',').strip()
        # ��������� �������� ������ �� payload
        try:
            object = row[3].split('Account Domain',1)[-1].split('Account Name: ',1)[-1].split('Account Name: ',1)[-1].split(' Account',1)[0]
        except:
            object = 'None'
        outstr = outstr + ';' + object.replace(';',',').strip()
        outstr = outstr + ';' + row[2].replace(';',',').strip()
        # ��������� ��� ������������ �� payload, ���� �� ��������� ������� payload ��� ����
        try:
            info = string.capwords(row[3].lower().split('cn=', 1)[-1].split(',ou=',1)[0])
        except:
            info = row[3]
        outstr = outstr + ';' + info.replace(';',',').strip()
        out.write(outstr + '\n')
        row = cursor.fetchone()
out.close()
# ---
# Local group change
tabheader=u'\n\n\n��������� ��������� ����� �� ������ ' + startdate + ' - ' + enddate + '\n\n'

with codecs.open(outfullpath, 'a', encoding=mycharset) as out:
     out.write(tabheader + colheader) 
     # in this cause ossec agent don't recognize account name by SID, so I use SID as "member"
     what = "userdata3 as action, convert_tz(timestamp,'+00:00'," + mytz +") as time, username as operator, inet_ntoa(conv(HEX(ip_src), 16, 10)) as source, data_payload as info from acid_event join extra_data on (acid_event.id=extra_data.event_id)"
     where = "acid_event.plugin_id=7107 and (acid_event.plugin_sid=18207 or acid_event.plugin_sid=18208)"
     select="select " + what + " where " + where + " and " + when  + " order by time"
     cursor.execute(select)
     row = cursor.fetchone() 
     while row:
        outstr = row[0].replace(';',',').strip()
        outstr = outstr + ';' + str(row[1]).replace(';',',').strip()
        outstr = outstr + ';' + row[2].replace(';',',').strip()
        # ��������� �������� ������ �� payload
        try:
            object = row[4].split('Group Name: ',1)[-1].split('Group',1)[0]
        except:
            object = 'None'
        outstr = outstr + ';' + object.replace(';',',').strip()
        outstr = outstr + ';' + row[3].replace(';',',').strip()
        # ��������� ��� ������������ �� payload, ���� �� ��������� ������� payload ��� ����
        try:
            info = row[4].split('Member: ', 1)[-1].split(' Account',1)[0]
        except:
            info = row[4]
        outstr = outstr + ';' + info.replace(';',',').strip()
        out.write(outstr + '\n')
        row = cursor.fetchone()
out.close()
# ---
# --- End of All
conn.close()
