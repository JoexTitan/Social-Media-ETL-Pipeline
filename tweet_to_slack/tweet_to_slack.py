import time
import slack
import datetime
import asyncio
import nest_asyncio
import pandas as pd
from sqlalchemy import create_engine

HOST_POSTGRES, PORT_POSTGRES = 'postgresdb', '5432'
DBNAME_POSTGRES, table = 'twitter_database', 'tweets_data'
USERNAME, PASSWORD = 'admin', 'admin'

while True:

    time.sleep(3600)

    connection_string = 'postgres://admin:admin@postgresdb:5432/twitter_database'
    engine_postgres = create_engine(connection_string)

    query = f'''SELECT * FROM {table}
    WHERE time > (SELECT MAX(time)-INTERVAL 'X hour' FROM {table})
    ;'''

    df_recent = pd.read_sql(query, engine_postgres)

    print("Recent data loaded")
    print(df_recent.shape)

    market_sentiment = round(df_recent['sentiment'].value_counts()* 100/df_recent['sentiment'].count(),2)

    TEXT = f'''{datetime.datetime.now()} : The crypto Market is currently {market_sentiment['neutral']}% neutral,
    {market_sentiment['positive']}% bullish and {market_sentiment['negative']}% bearish.
    '''

    print(Text)
    
    nest_asyncio.apply()

    #Need to register an app at slack.api and get 'Bot User OAuth Access Token'
    token = '...'
    client = slack.WebClient(token=token)

    response = client.chat_postMessage(channel='#slackbot_testing', text=TEXT)
