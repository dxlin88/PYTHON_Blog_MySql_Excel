import re
import requests
import json
import time
import datetime

import pymysql
from sshtunnel import SSHTunnelForwarder

server =SSHTunnelForwarder(
	ssh_address_or_host=('172.81.215.61',22),
	ssh_username='root',
	ssh_password='lindx@550909',
	remote_bind_address=('localhost',3306)
)
server.start()
print("server started")

db=pymysql.connect(
	host="localhost",
	port=server.local_bind_port,
	user="root",
	passwd="550909",
	db="blogReview",
	charset="utf8")
print("DB connected")
cursor=db.cursor()

wenzhangID=[ ]
wenzhangName=[ ]

print("Reading Blog.....")

for i in range(1,5):
    url="http://blog.sina.com.cn/s/article_sort_1313777975_10001_"+str(i)+".html"
   
    html=requests.get(url)
    strr=html.content.decode()
    
    pat2=re.compile(r'id="t_10001_\w{10}(.*?)"')
    pat1=re.compile(r'.html">(.*?)</a></div>')
   
    namelist=pat1.findall(strr)
    idlist=pat2.findall(strr)

    wenzhangName.extend(namelist)
    wenzhangID.extend(idlist)
IDall=','.join(wenzhangID)
#print(IDall)

url="http://comet.blog.sina.com.cn/api?maintype=num&uid=4e4ea937&aids="+IDall
# print(url)

html=requests.get(url)

strr=html.content.decode()
# print(strr)

pat3=re.compile(r'se\W\W\W\W(.*?)\)')
pat3dict=pat3.findall(strr)

#print(type(pat3dict[0]))
#print(pat3dict[0])

patt= pat3dict[0]
data=json.loads(patt)


#新建表
# sql="""create table student(
# 	id int not null,
# 	name varchar(20),
# 	age int

#表中加数据
print("Data to DB")
print()
print("Processing Result:")
sql='SELECT blog.clickcount FROM blog WHERE to_days(NOW())-to_days(time)=1'
cursor.execute(sql)
datayestoday = cursor.fetchall()
for i in range(0,len(wenzhangName)):
    BlogName = wenzhangName[i].replace('&nbsp;',' ')
    BlogCount = data[wenzhangID[i]]["r"]
    BlogID = wenzhangID[i]
    sql=('insert into blog(time,filename,fileID,clickcount) values(now(),%s,%s,%s)')
    cursor.execute(sql,(BlogName,BlogID,BlogCount))

    datadiffe=(BlogCount-datayestoday[i][0])
    if datadiffe !=0:
   		 print(BlogName,datadiffe)
db.commit()

#数据分析
sql='SELECT SUM(blog.clickcount) FROM blog WHERE TO_DAYS(time)=TO_DAYS(NOW())'
cursor.execute(sql)
sumToday = cursor.fetchone()
sql='SELECT SUM(blog.clickcount) FROM blog WHERE to_days(NOW())-to_days(time)=1'
cursor.execute(sql)
sumyestoday = cursor.fetchone()
sql='SELECT SUM(blog.clickcount) FROM blog WHERE to_days(NOW())-to_days(time)=2'
cursor.execute(sql)
sumbeforeyestoday = cursor.fetchone()
TodayAdd=sumToday[0]-sumyestoday[0]
YestodayAdd=sumyestoday[0]-sumbeforeyestoday[0]
print()
print("BlogCount Total ",sumToday[0])
print("TodayClick Change",TodayAdd)
print("LoopRate is",TodayAdd-YestodayAdd)
cursor.close()
db.close()
print()
print('DBclosed')