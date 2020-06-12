#credential file with keys
import credential
import oauth2 as oauth
import json
import re
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
import xlwt 
from xlwt import Workbook 


# credential can be stored as config file, or in a database, or in environemt variable
CONSUMER_API_KEY = credential.consumer_key
API_SECRET_KEY = credential.consumer_secret
ACCESS_TOKEN = credential.access_token
ACCESS_TOKEN_SECRET= credential.access_token_secret

class OauthClient():
  def __init__(self):
    self.consumer = oauth.Consumer(CONSUMER_API_KEY, API_SECRET_KEY)
    self.access_token = oauth.Token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    self.client = oauth.Client(self.consumer, self.access_token)

  def get_tweets(self, query='%23atamnirbharbharat', count=100, lang='en', result_type='mixed', tweet_mode='extended'):
    search_endpoint = "https://api.twitter.com/1.1/search/tweets.json?q={}&result_type={}&count={}&lang={}&tweet_mode={}".format(query, result_type, count,lang, tweet_mode)
    response, data = self.client.request(search_endpoint)
    tweets = json.loads(data)
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
def save_workbook(sentiment_result, sheet_name='result'):
  wb = Workbook()
  sheet = wb.add_sheet(sheet_name) 

  row = 1
  sheet.write(0,0, "Tweets")
  sheet.write(0,1, "Sentiment_Type")
  for data in sentiment_result:
    print(data)
    sheet.write(row, 0, data[0])
    sheet.write(row, 1, data[1])
    row = row+1
    
  wb.save('tweets.xls') 


if __name__ == "__main__":
  client=OauthClient()
  popular_tweets= client.get_tweets(result_type="popular")
  recent_tweets= client.get_tweets(result_type="recent")
  tweets_list = popular_tweets + recent_tweets
  cleaned_list = clean_tweets(tweets_list)
  sentiment_result = [(tweet, get_sentiment(tweet)) for tweet in cleaned_list]
  save_workbook(sentiment_result)