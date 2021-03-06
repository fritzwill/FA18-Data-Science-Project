import time, tweepy, os, sys
from textblob import TextBlob
import json

### DICT MAPS NONCONTINUOUS TWEET FILES TO NONCONTINUOUS STOCK DATA ###
map_dict = {1:'2018-10-05',2:'2018-10-08',3:'2018-10-08',4:'2018-10-09',5:'2018-10-10',6:'2018-10-11',\
            7:'2018-10-12',8:'2018-10-15',9:'2018-10-15',10:'2018-10-22',11:'2018-10-22',12:'2018-10-22',13:'2018-10-22',\
            14:'2018-10-23',15:'2018-10-25',16:'2018-10-29',17:'2018-10-30',18:'2018-11-01',19:'2018-11-02',20:'2018-11-05',\
            21:'2018-11-06',22:'2018-11-07',23:'2018-11-08'}

### READ STOCK INFO ###
stocks = {}
with open('stock_prev_info.csv','r+') as f:
    text = f.readlines()
    for line in text:
        split = line.split(',')
        try:
            stocks[split[0]].append(split[1:])
        except:
            stocks[split[0]] = [split[1:]]

def touch(path):
    with open(path,'a'):
        os.utime(path,None)

if __name__ == "__main__":
    ### GRAB COMPANY DATA ###
    line = []
    with open('companies.csv',"r+") as f:
        lines = f.readlines()
    f.close()
    titles = ["name","ticker","ceo"]
    ### FOR EVERY DAY ###
    for DAY in range(4,26):
        ### INITS ###
        n = 0
        sum = 0
        total_followers = 0.0000
        stock_data_point = []
        date = map_dict[DAY-3]
        ### LOOP OVER COMPANIES ###
        for line in lines:
            query = line.split(',')
            company = query[1]
            ### FORMAT KEYWORD.TXT TITLES ###
            for i in range(1,len(query)-2):
                titles.append("key{0}".format(i))
            ### FIND MATCHING STOCK DATA POINT ###
            for line in stocks[company]:
                print(line)
                print(date)
                if str(line[3])==str(date):
                    stock_data_point = line
            ### GENERATE FEATURES ###
            print(stock_data_point)
            change = float(stock_data_point[4])-float(stock_data_point[3])
            openValue =  float(stock_data_point[3])
            writeData = []
            ### LOOP OVER TWEETS.TXT FOR A DAY BY SEARCH WORD ###
            for i in range(0,len(query)-1):
                readPath = "data/tweets/d{0}/{1}-{2}.txt".format(str(DAY),query[0],titles[i])
                if (i==1):
                    print(query[i])
                    try:
                        ### READ IN DESIRED TWEET FILE(S) ###
                        data = []
                        with open(readPath,'r') as fp:
                            data = fp.readlines()
                        ### FIND TOTAL FOLLOWERS ###
                        for twt in data:
                            try:
                                tweet = json.loads(twt)
                                total_followers+=int(tweet['user']['followers_count'])
                            except UnicodeEncodeError:
                                continue
                        ### GENERATE PROPORTIONAL dVALUE ###
                        for twt in data:
                            tweet = json.loads(twt)
                            date = tweet['date']
                            testimonial = TextBlob(ascii(tweet['text']))
                            polarity, confidence = testimonial.sentiment
                            value = polarity*confidence*float(float(tweet['user']['followers_count'])/float(total_followers))*float(change/openValue)
                            writeData.append('{0},{1},{2},{3}'.format(tweet['user']['follower_count'],polarity,confidence,value))
                    ### EXCEPTION ###
                    except FileNotFoundError:
                        continue

            ### WRITE TO ClEAN TEXT FILE ###
            writePath ="data/clean/d{0}/{1}-cleaned.csv".format(DAY-3,query[0])
            print('Writing to {0} . . .'.format(writePath))
            exists = os.path.isfile(writePath)
            ### TOUCH IF NOT WRITTEN ###
            if (exists==False):
                touch(writePath)
            writeFp = open(writePath,'a')
            ### WRITE DATA ###
            for data in writeData:
                writeFp.write(data)
            writeFp.close()
