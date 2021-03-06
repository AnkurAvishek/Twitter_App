# -*- coding: utf-8 -*-
from flask import Flask, render_template, send_from_directory, request
import xlwt
from xlwt import Workbook
import credential
import oauth2 as oauth
import json
import re
import os
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
import pandas as pd

app = Flask(__name__, template_folder= "templates")

CONSUMER_API_KEY = credential.consumer_key
API_SECRET_KEY = credential.consumer_secret
ACCESS_TOKEN = credential.access_token
ACCESS_TOKEN_SECRET= credential.access_token_secret

#import os
#try:
#    CONSUMER_API_KEY = os.environ['consumer_key']
#    API_SECRET_KEY  = os.environ['consumer_secret']
#    ACCESS_TOKEN = os.environ['access_token']
#    ACCESS_TOKEN_SECRET = os.environ['access_token_secret']
#except:
#    print("environmet variables not defined")

class OauthClient():
  def __init__(self):
    self.consumer = oauth.Consumer(CONSUMER_API_KEY, API_SECRET_KEY)
    self.access_token = oauth.Token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    self.client = oauth.Client(self.consumer, self.access_token)

  def get_tweets(self, query='#twitter', count=10, lang='en', result_type='mixed', tweet_mode='extended'):
    search_endpoint = "https://api.twitter.com/1.1/search/tweets.json?q={}&result_type={}&count={}&lang={}&tweet_mode={}".format(query, result_type, count,lang, tweet_mode)
    response, data = self.client.request(search_endpoint)
    tweets = json.loads(data)
    #print(response)
    #print(tweets)
    if 'statuses' not in tweets:
        return []
    tweets_list = []
    for tweet in tweets['statuses']:
        tweets_list.append(tweet['full_text'])
        #print(tweet['full_text'])
    return tweets_list

def clean_tweets(tweets_list):
  cleaned_list = []
  for tweet in tweets_list:
    clean_tweet = re.sub("(RT @\w+)|(@\w+)|(https:\/\/t.co\/\w+)|([^a-zA-Z0-9\s\.\!%,])","", tweet)
    cleaned_list.append(clean_tweet)
  return cleaned_list

# Get Tweets Sentiment
def get_sentiment(text):
  #try:
  blob = TextBlob(text,  analyzer=NaiveBayesAnalyzer())
  if blob.sentiment.p_pos >= blob.sentiment.p_neg:
      return 'Positive'
  else:
      return 'Negative'    
  #except:
    #print("exception occured")
    #return ""

#Save workbook    
def save_workbook(sentiment_result, tweets_list, sheet_name='result'):
  #wb = Workbook()
  #sheet = wb.add_sheet(sheet_name) 

  #row = 1
  #sheet.write(0,0, "Tweets")
  #sheet.write(0,1, "Sentiment_Type")
  #for data in sentiment_result:
    #print(data,"write to sheet row:", row, data[0])
    #sheet.write(row, 0, data[0])
    #sheet.write(row, 1, data[1])
    #row = row+1
  #print(wb)
  try:
    os.remove('./output.xls')
  except:
    pass
  #wb.save('./tweets.xls')
  df1 = pd.DataFrame(sentiment_result, columns =['Tweet', 'Sentiment'])
  df2 = pd.DataFrame(tweets_list, columns=['Tweets'])
  df = pd.concat([df2['Tweets'], df1['Sentiment']], axis=1)
  df.to_excel("./output.xlsx", sheet_name=sheet_name, index=False)
  return
  

@app.route('/')
def home():
    return render_template('home.html', result=False)
    
@app.route('/get_tweets', methods=['POST','GET'])
def result():
    print(request)
    hashtag = request.form['hashtag']
    if hashtag=='':
        return render_template('home.html', result=False)
    print(hashtag,"---------------", type(hashtag))
    if re.match('^#.*', hashtag):
        hashtag = re.sub('#', '', hashtag)
    client=OauthClient()
    popular_tweets= client.get_tweets(query=hashtag, result_type="popular")
    recent_tweets= client.get_tweets(query=hashtag, result_type="recent")
    tweets_list = popular_tweets + recent_tweets
    #print("\n Tweets_list ----\n", tweets_list)
    cleaned_list = clean_tweets(tweets_list)
    print("\n Cleaned List----\n", cleaned_list)
    sentiment_result = [(tweet, get_sentiment(tweet)) for tweet in cleaned_list]
    #print("\n Sentiment Result---\n", sentiment_result)
    save_workbook(sentiment_result, tweets_list)    
    return render_template('result.html', result=True)


@app.route('/download')
def download():
    return send_from_directory('./','output.xlsx', as_attachment=True,  cache_timeout=0)
 
@app.errorhandler(404)  
def _404(e): 
    return render_template('home.html', result=False)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)

