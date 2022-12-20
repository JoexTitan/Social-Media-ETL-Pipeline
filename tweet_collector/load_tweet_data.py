import json
import pandas as pd
import datetime
from config import cfg
import pymongo
from tweepy import OAuthHandler, Stream
from tweepy.streaming import StreamListener

HOST, PORT = 'localhost', '27017'
CLIENT = pymongo.MongoClient('mongodb')
DB = CLIENT.twitter_db

def authenticate():
    auth = OAuthHandler(cfg['CONSUMER_API_KEY'], cfg['CONSUMER_API_SECRET'])
    auth.set_access_token(cfg['ACCESS_TOKEN'],cfg['ACCESS_TOKEN_SECRET'])
    return auth

def write_tweet(tweet_dict):

    df = pd.DataFrame(data= tweet_dict, index=[0])
    df.to_csv('db_bitcoin.csv', mode='a', header=None)

def load_into_mongo(t):
    DB.tweets.insert(t)
    print(f"Successfully loaded tweet by {t['username']}into Mongo!")

class TwitterStreamer(StreamListener):
    def get_hashtags(self, t):
            hashtags = []
            if 'extended_tweet' in t:
                for hashtag in t['extended_tweet']['entities']['hashtags']:
                    hashtags.append(hashtag['text'])
            elif 'hashtags' in t['entities'] and len(t['entities']['hashtags']) > 0:
                hashtags = [item['text'] for item in t['entities']['hashtags']]
            else:
                hashtags = []
            return hashtags

    def get_media(self, t):
            media_url = []
            if 'extended_tweet' in t and 'media' in t['extended_tweet']['entities']:
                for media in t['extended_tweet']['entities']['media']:
                    media_url.append(media['media_url_https'])
                    media_type = media['type']
            else:
                media_url = None
                media_type = ''
            return media_url, media_type

    def get_tweet_dict(self, t):
            if 'extended_tweet' in t:
                text = t['extended_tweet']['full_text']
            else:
                text = t['text']
            hashtags = self.get_hashtags(t)
            media_url, media_type = self.get_media(t)
            time_temp = datetime.datetime.now()
            tweet = {'created_at': t['created_at'],
                     'id': t['id_str'],
                     'text': text,
                     'username': t['user']['screen_name'],
                     'followers':t['user']['followers_count'],
                     'user_favorites_count': t['user']['favourites_count'],
                     'retweets': t['retweet_count'],
                     'favorites': t['favorite_count'],
                     'time': time_temp}
            return tweet

    def on_data(self, data):
        tweet = json.loads(data)
        if tweet['retweeted'] == False and 'RT' not in tweet['text'] and tweet['in_reply_to_status_id'] == None:
            tweet = self.get_tweet_dict(tweet)
            if tweet['followers'] > 2000:
                load_into_mongo(tweet)

    def on_error(self, status):
        if status == 420:
            print(status)
            return False

if __name__ == '__main__':
    auth = authenticate()
    streamer = TwitterStreamer()
    stream = Stream(auth, streamer)
    stream.filter(track=['bitcoin'], languages=['en'])
