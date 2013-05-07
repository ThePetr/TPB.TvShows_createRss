#! /usr/bin/env python
#Created By ThePetr ©2013
from bs4 import BeautifulSoup
import re, os,time, urllib2, sys
from datetime import datetime, date
Series=["Arrow","Breaking Bad","Dexter","How I Met Your Mother","The Big Bang Theory",\
"The Walking Dead","True Blood", "Vicious"]
verbose=False
numberOfSites=101
saveName="TPB_mySeries.xml"
for arg in sys.argv:
  if arg=="-v" or arg=="-V":
		print "Verbose mode is on\n"
		noia=0															#noia=number of items added
		verbose=True
	elif arg.isdigit():
		if int(arg)<101:
			numberOfSites=int(arg)
	elif arg=="-h" or arg=="-H":
		print "\
HOW-TO:\n\
-h -H: This message\n\
-v -V: Verbose mode ON (standard=OFF)\n\
integer (a number): how many of the browse sites you want to get, top 100 is automaticaly done last.\n\
i.e. python TPBrss.py 50  means the first 48 pages and the top 100 page as well\n\
selfChosenName.xml: save the output as this file\n\
i.e. python TPBrss.py feed.xml  will save the output as feed.xml"
		sys.exit()
	elif re.compile(".*\.xml").match(arg):
		saveName=arg
		
site="http://pirateproxy.net/browse/205/"
Titles=[]
######### Begin building XML ###########
rssBuilder=""
rssBuilder="\
<?xml version='1.0' encoding='utf-8'?><rss version='2.0' xmlns:atom='http://www.w3.org/2005/Atom'>\n\
<channel>\n\
	<title>TPB Top 100 - TV shows</title>\n\
	<link>http://pirateproxy.net/top/205</link>\n\
	<description>The top 100 Tv-Shows from The Pirate Bay</description>\n\
	<language>en</language>\n\
	<generator>My Mind, and a couple nights of python</generator>\n\
	<docs>http://blogs.law.harvard.edu/tech/rss</docs>\n\
	<lastBuildDate>%s</lastBuildDate>\n" % (datetime.fromtimestamp(time.time()).strftime("%a, %d %b %Y %X")+' +0100')
######### Pause Building XML #############
#--------------------------------------------------
for c in range(0,int(numberOfSites)):
	if c==100 or (numberOfSites<101 and c==numberOfSites-1):
		soup=BeautifulSoup(urllib2.urlopen("http://pirateproxy.net/top/205"))
	else:
		soup=BeautifulSoup(urllib2.urlopen(site+"/"+str(c)+"/3"))
		
	######### Begin Gathering needed Info #############
	for el in soup.findAll('tr'):									#loop through all tr elements
		detName = el.find('div', {'class':'detName'})				#find div with class detName
		if detName is None:     									# not in this tr
			continue												#jump out of this iteration to the next one
		else:                   									
			title=detName.text 										#get title
			aLinks=el.find_all("a") 								#get all links
			for link in aLinks:										#loop through all the links in this tr
				if link.get("href")[0:6]=="magnet":					#if first 6 letters in the link are magnet we've got the magnet
					magnetLink=link.get("href")						#save tha magnet link in variable
				elif link.get('href')[0:6]=="/user/":				#if first six letters are /user/ we've got the user... you understand that right :D
					user=link.get("href")[6:]						#save the username in variable
			########### Begin DATE #############					#whole lot of schit to get date <_<'
			mdate=el.find('font', {'class':'detDesc'}).text.partition("Uploaded ")[2].partition(", Size")[0]
			mdate=re.sub("&nbsp;|\xA0", " ", mdate)					#replace unicode space with regular ones
			fDate=datetime.now()
			timePattern="%a, %d %b %Y %H:%M:%S"
			# "M mins ago" - e.g. "7 mins ago" 
			if re.compile('^([0-6]?[0-9]) mins ago$').match(mdate):
				min=mdate.partition(" mins ago")[0]
				tmpDate=datetime.fromtimestamp(time.time()-int(min)*60)
				fDate=tmpDate.strftime(timePattern)#[:-3]
			# "Today HH:MM" - e.g. "Today 08:24"
			elif re.compile("^Today [0-9]{2}:[0-9]{2}$").match(mdate):
				hours=mdate.partition("Today ")[2].partition(":")[0]
				min=mdate.partition("Today ")[2].partition(":")[2]
				now=datetime.now()
				tmpDate=datetime(now.year,now.month,now.day,int(hours),int(min),0)
				fDate=tmpDate.strftime(timePattern)#[:-3]
			# "Y-day HH:MM" - e.g. "Y-day 16:23"
			elif re.compile("^Y-day [0-9]{2}:[0-9]{2}$").match(mdate):
				hours=mdate.partition("Y-day ")[2].partition(":")[0]
				min=mdate.partition("Y-day ")[2].partition(":")[2]
				now=datetime.now()
				if now.day==1:
					if now.month==1:
						now.year-=1
					else:
						now.month-=1
				tmpDate=datetime(now.year,now.month,now.day,int(hours),int(min),0)
				fDate=tmpDate.strftime(timePattern)#[:-3]
			# "mm-dd HH:MM" - e.g. "11-16 01:06"
			elif re.compile("^[01][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]$").match(mdate):
				month=mdate.partition(" ")[0].partition("-")[0]
				day=mdate.partition(" ")[0].partition("-")[2]
				hour=mdate.partition(" ")[2].partition(":")[0]
				min=mdate.partition(" ")[2].partition(":")[2]
				tmpDate=datetime(datetime.now().year,int(month),int(day),int(hour),int(min),0)
				fDate=tmpDate.strftime(timePattern)#[:-3]		
			# "mm-dd YYYY" - e.g. "08-14 2004"
			elif re.compile("^[01][0-9]-[0-3][0-9] [0-9]{4}$").match(mdate):
				month=mdate.partition(" ")[0].partition("-")[0]
				day=mdate.partition(" ")[0].partition("-")[2]
				year=mdate.partition(" ")[2]
				tmpDate=datetime(int(year),int(month),int(day))
				fDate=tmpDate.strftime(timePattern)#[:-3]
			else:
				fDate=fDate.strftime(timePattern)#[:-3]
			######### End DATE #######################				#now date is in fDate YaaY :3
			#-----------------------------------------
			######### Got All info ###################
			######### Trimming All info ##############
			title=title.strip()
			magnetLink=magnetLink.strip()
			fDate=fDate.strip()
			user=user.strip()
			##########################################
			######### Continue Building XML ##########				#make an rss item for every tr item in loop
			if not title in Titles:
				if not "1080p" in title and not "720p" in title:
					if "eztv" in user:
						for serie in Series:
							if serie in title:	
								if verbose==True:
									noia+=1
								Titles.append(title)
								rssBuilder+="\
	<item>\n\
		<title>%s</title>\n\
		<link><![CDATA[%s]]></link>\n\
		<pubDate>%s</pubDate>\n\
		<author>%s</author>\n\
	</item>\n" %(title,magnetLink,fDate+' +0200',user)
	if verbose==True:
		print "site "+str(c)+" done"
		print "Added "+str(noia)+" items\n"
		noia=0
		
rssBuilder+="</channel></rss>"									#end the xml file with appropriate file tags
xmlFile=open(saveName,"w")
xmlFile.write(rssBuilder)
xmlFile.close
soup.close
