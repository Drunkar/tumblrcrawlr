#coding: utf-8

import json
import urllib
import os
import time
from datetime import datetime
from datetime import timedelta
import codecs

import oauth2

CONSUMER_KEY = 'YOUR_CONSUMER_KEY'
CONSUMER_SECRET = 'YOUR_CONSUMER_SECRET'

ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN'
ACCESS_TOKEN_SECRET = 'YOUR_ACCESS_TOKEN_SECRET'

def main():
    base_hostname = 'your_blog.tumblr.com'  # blogname
    tag           = 'your_favorite_tag'     # tag   
    rate          = 20                          # clowl rate(m)
    rebloged      = []                          # rebloged picture URL

    # ignore list
    ignoreList = "ignore.txt"
    loadIgnoreList(ignoreList, rebloged)

    # log file
    fileName = base_hostname+'_' + str(datetime.now().strftime('%Y%m%d_%H%M%S')) +'.csv'
    logCSV = codecs.open(fileName, 'w', 'utf-8')
    startTime = datetime.now()
    fileDuration = timedelta(days=1)

    consumer = oauth2.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)


    while True:
        print "クロール開始"
        token = oauth2.Token(key=ACCESS_TOKEN,
                             secret=ACCESS_TOKEN_SECRET)

        fields = getfieldsForTagged(tag, consumer, token)
        # id, reblog_keys, state, tags, imageurl, date
        # print idAndKeys

        reblog(fields, base_hostname, consumer, token, rebloged, logCSV)

        saveIgnoreList(ignoreList, rebloged)

        # if the process takes longer than fileduration, make a new file.
        if(datetime.now() - startTime > fileDuration):
            logCSV.close()
            os.system("mv "+filename+" log/")
            fileName = base_hostname+'_' + str(datetime.now().strftime('%Y%m%d_%H%M%S')) +'.csv'
            logCSV = codecs.open(fileName, 'w', 'utf-8')
            startTime = datetime.now()

        time.sleep(rate*60)

    logCSV.close()

def loadIgnoreList(ignoreList, rebloged):
    fi = codecs.open(ignoreList, 'r', 'utf-8')
    for line in fi:
        rebloged.append(line.rstrip())
    fi.close()

def saveIgnoreList(ignoreList, rebloged):
    fi = codecs.open(ignoreList, 'w', 'utf-8')
    for item in rebloged:
        fi.write(item + "\n")
    fi.close()

def getfieldsForTagged(tag, consumer, token):
    # for tag search
    url = 'http://api.tumblr.com/v2/tagged?tag='+tag+'&api_key='+CONSUMER_KEY
    # for dashboard
    # url = 'http://api.tumblr.com/v2/user/dashboard/tagged/gif'
    params = {}
    client = oauth2.Client(consumer, token)
    resp, content = client.request(url, method='GET', body=urllib.urlencode(params))
    dsbd= json.loads(content)
    # print json.dumps(dsbd, indent=2)
    
    # for tag search
    return [{'reblog_key': obj['reblog_key'], 'id': obj['id'], 'state': obj['state'],
             'tags': obj['tags'], 'url':obj['photos'][0]['original_size']['url'], 'date': obj['date']}
             for obj in dsbd['response'] if 'photos' in obj]

    # for dashboard
    # return [obj['photos'][0]['original_size']['url'] for obj in dsbd['response']['posts'] if 'photos' in obj]

def  writeLog(fields, logCSV):
    for field in fields:
        dataRow = datetime.now().strftime('%Y-%m-%d,%H:%M:%S')+',' \
                    +str(field['id'])+','+str(field['state'])+','  \
                    +str(field['tags'])+','+str(field['url'])+','  \
                    +str(field['date'])+'\n'
        logCSV.write(dataRow)

def reblog(fields, base_hostname, consumer, token, rebloged, logCSV):
    
    url = 'http://api.tumblr.com/v2/blog/'+base_hostname+'/post/reblog'
    client = oauth2.Client(consumer, token)

    for field in fields:
        if field['url'] in rebloged:
            print field['url'], 'was rebloged.'
            continue
        else:
            params = { 
                'id': field['id'],
                'reblog_key': field['reblog_key']
            }
            resp, content = client.request(url, method='POST', body=urllib.urlencode(params))

            if len(rebloged) > 10000: del rebloged[0]
            rebloged.append(field['url'])
            writeLog

            print "reblog{ id: "+str(field['id'])+", reblog_key: " \
                                +str(field['reblog_key'])+" }"


if __name__ == '__main__':
    main()