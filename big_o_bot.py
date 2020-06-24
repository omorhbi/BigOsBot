import tweepy
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
import time
from keys import *
import os, random
from nltk import word_tokenize, pos_tag

# API and authentication set up
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

# files used for this bot
FILE_NAME = 'last_seen_id.txt'
NOUN_FILE = 'nounlist.txt'

# get the last seen id
def get_last_seen_id(file):
    file_read = open(file, 'r')
    if os.stat(file).st_size == 0:
        return
    last_seen_id = int(file_read.read().strip())
    file_read.close()
    return last_seen_id

# store the last seen id
def store_last_seen_id(last_seen_id, file):
    file_write = open(file, 'w')
    file_write.write(str(last_seen_id))
    file_write.close()
    return

# increment variable used to detect when the bot should post
increment = 0

# this is for checking if a word's tag is included here
noun_tags = ['NN', 'NNS', 'NP', 'NPS', 'NNP']


def replying_posting_tweets(increment):
    valid_request = False
    print ("replying to tweets")

    # this indicates 2 hours have passed, meaning the bot will post its automated tweet
    if increment == 360:
        lines = open(NOUN_FILE).read().splitlines()
        random_line = random.choice(lines)
        #print(random.choice(lines))
        api.update_status(f'#Big{random_line}')

    print(increment, "increment")
    # gets the last seen id
    last_seen_id = get_last_seen_id(FILE_NAME)

    mentions = api.mentions_timeline(
                            last_seen_id,
                            tweet_mode = 'extended')
    
    for mention in reversed(mentions):

        last_seen_id = mention.id
        
        # store the last seen id
        store_last_seen_id(last_seen_id, FILE_NAME)
        token = word_tokenize(mention.full_text)
        #print(token)
        
        # checks if the request is too long or has no inputted word
        if len(token) > 4 or len(token) == 2:
            print("Invalid request.")
            api.update_status(f"@{mention.user.screen_name} Sorry, I can't do that. Make sure to have at most two words.", mention.id) 
            continue

        # if length of list is 3
        if len(token) == 3:
            tags = nltk.pos_tag(token)
            print(tags)
            if tags[2][1] in noun_tags:
                # temporary
                print("valid noun. Responding back...")
                response = token[2]
                api.update_status(f'@{mention.user.screen_name} Big {response}', mention.id)
                
            if tags[2][1] not in noun_tags:
                api.update_status(f'@{mention.user.screen_name} Invalid request. Please ensure the word you provide is a noun',
                                    mention.id)
                
        # if length of list is 4
        if len(token) == 4:
            tags = nltk.pos_tag(token[2:4])
            print(tags)
            for word in tags:
                if word[1] not in noun_tags:
                    print("invalid noun")
                    api.update_status(f'@{mention.user.screen_name} Big {response}', mention.id)
                    valid_request = False
                    break
                valid_request = True

            if valid_request == True:
                response = ' '.join(map(str,token[2:4]))
                print("valid noun. Responding back...")
                print(mention.user.screen_name)
                api.update_status(f'@{mention.user.screen_name} Big {response}', mention.id)

            if valid_request == False:
                print("Invalid noun here.")
                api.update_status(f"@{mention.user.screen_name} Invalid request. Please ensure that the words you provide makes a noun phrase",
                              mention.id)
            
        print(str(mention.id) + ' - ' + mention.full_text)

    return increment

while True:
    replying_posting_tweets(increment)
    if increment == 360:
        increment = 0
    increment += 1
    time.sleep(20)
