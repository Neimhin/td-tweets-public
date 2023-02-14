#!/usr/bin/env python3
import sys
import os
import re
from pandas import DataFrame
import tweepy

api_key=""
api_secret_key=""
bearer=""
access_token=""
access_token_secret=""

auth = tweepy.OAuthHandler(api_key,api_secret_key)
auth.set_access_token(access_token,access_token_secret)

api = tweepy.API(auth)
userID = sys.argv[2] if len(sys.argv) > 2 else "seansherlocktd"

os.mkdir(f"data/{userID}")

def print_tweets(tw):
    outtweets=[[tweet.id_str,
                tweet.created_at,
                re.sub('[\n\t]', ' ',tweet.full_text.encode("utf-8").decode("utf-8"))]
                for idx, tweet in enumerate(tw)]
    df = DataFrame(outtweets, columns=["id","created_at","full_text"])
    df.to_csv(f'data/{userID}/to-{oldest_id}.tsv',sep='\t',index=False)



cursor_file = f"data/{userID}/oldest-id"
def oldest_id_load():
    try:
        with open(cursor_file, "r") as f:
            return int(f.read())
    except OSError:
        return None

def oldest_id_save(ID):
    with open(cursor_file, "w") as f:
        f.write(str(ID))
        return ID

def fetch_tweets():
    return api.user_timeline(screen_name=userID,
        count=count_per_req,
        max_id=oldest_id -1 if oldest_id else None,
        include_rts = False,
        tweet_mode='extended')

oldest_id = oldest_id_load()
count_per_req = max(1,min(int(sys.argv[1]),200)) if len(sys.argv) > 1 else 1
total = 0
tweets =  fetch_tweets()

while len(tweets) > 0:
    try:
        oldest_id = tweets[-1].id
        oldest_id_save(oldest_id)
        total = total + len(tweets)
        print("Total: ", total, file=sys.stderr)
        print_tweets(tweets)
        tweets = api.user_timeline(screen_name=userID,
            count=count_per_req,
            max_id=oldest_id - 1,
            include_rts = False,
            tweet_mode='extended')
    except tweepy.errors.TooManyRequests:
        print("sleeping 15*60",file=sys.stderr)
        time.sleep(15*60)
