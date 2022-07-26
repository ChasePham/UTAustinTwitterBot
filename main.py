import tweepy
from textblob import TextBlob
import time
import random


all_keys = open('Keys', 'r').read().splitlines()
CONSUMER_KEY = all_keys[0]
CONSUMER_SECRET_KEY = all_keys[1]
ACCESS_TOKEN = all_keys[2]
ACCESS_SECRET_TOKEN = all_keys[3]
BEARER_TOKEN = all_keys[4]


auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET_TOKEN)
api = tweepy.API(auth, wait_on_rate_limit=True)


# Retrieves the latest ID within the text file, this allows the code to not repeat retweets through
# the many @'s the bot may receive.
def get_newest_id(file='Last_seen_text.txt'):
    file_read = open(file, 'r')
    newest_id = int(file_read.read().strip())
    file_read.close()
    return newest_id


# Once a new @ mention is brought for the bot, it saves that text ID into the Last_seen_text.txt.
# The purpose is to update the latest @ mention constantly, so no repeats occur.
def save_newest_id(newest_id, file='Last_seen_text.txt'):
    file_write = open(file, 'w')
    file_write.write(str(newest_id))
    file_write.close()
    return


# Replies to @ mentions towards the bot in real time. Sends simple quotes, jokes, Hook'em's, or positive or bad
# mentions to the bot.
def reply_to_mentions():
    newest_seen_id = get_newest_id('Last_seen_text.txt')
    at_mentions = api.mentions_timeline(since_id=newest_seen_id)
    print("Finding and replying to mentions....")

    # Loops through the mentions from beginning to present time. Once present time hits
    # it will save that tweet within the text file.
    for current_mention in reversed(at_mentions):
        newest_seen_id = current_mention.id
        save_newest_id(newest_seen_id, 'Last_seen_text.txt')
        print(str(current_mention.id) + "-" + current_mention.text)
        api.create_favorite(id=current_mention.id)
        print("tweet is liked!\n")

        # Checks the tweet if it's giving a good or bad sentiment score
        mention_analysis = TextBlob(current_mention.text)
        mention_analysis_total = mention_analysis.sentiment.polarity
        print("Tweet has a sentiment score of: " + mention_analysis_total)
        analyze_mention_tweet(current_mention, mention_analysis_total)

    print("")


# Analyzes the mention of a tweet and checks with sentimental analysis if it is rude or good, then responds back
def analyze_mention_tweet(current_mention, mention_analysis_total):
    if "hook" in current_mention.text.lower():
        print("A Hook Em is found!")
        print("Currently responding back...")
        api.update_status(status='@' + current_mention.user.screen_name + ' Hook Em!!!',
                          in_reply_to_status_id=current_mention.id)
    elif mention_analysis_total < 0:
        print("Bad text sent, processing a response...")
        response = "I'm sorry, but I do not like your tweet :("
        api.update_status(status='@' + current_mention.user.screen_name + " " + response,
                          in_reply_to_status_id=current_mention.id)
    else:
        print("Returning a funny joke or quick fact...")
        all_lines = open('Quick_Facts.txt').read().splitlines()
        random_text = random.choice(all_lines)
        api.update_status(status='@' + current_mention.user.screen_name + " " + random_text,
                          in_reply_to_status_id=current_mention.id)


# Lists out generic info about a specific user
def find_individual_info(name):
    user = api.get_user(screen_name=name)
    print("The users follower count: " + str(user.followers_count))
    print("The users username: " + user.name)
    print("The users screen name: " + user.screen_name)
    print("The users locations: " + user.location)
    print("The users description: " + user.description)
    print("The users total listed accounts: " + str(user.listed_count))
    print("The users total number of friends: " + str(user.friends_count))
    print("The date when the user created the account: " + str(user.created_at))
    print('The user\'s url:  ' + user.url)
    print('Verified? ' + str(user.verified))


# finds generic info over a range of people
def find_list_info(list_of_following):
    for individual in list_of_following:
        find_individual_info(individual.screen_name)
        print("\n")


# Follows individual people and adds that to the list of followers
def follow_people(person):
    friends = api.get_friends(count=200)  # max
    listofusernames = []
    for individual in friends:
        listofusernames.append(individual.screen_name)
    if person == "" or person == " ":
        return listofusernames
    if not(person in listofusernames):
        api.create_friendship(screen_name=person)
        listofusernames.append(person)
        total = len(listofusernames)
        print("total people you follow: " + str(total))
        file = open("followlist.txt", "w")
        for names in listofusernames:
            file.write(names + "\n")
        file.close()
    else:
        print("You already follow: " + person)
    return listofusernames

# To find and locate tweets from friends, we can do the same process we did with finding and replying
# to @'s! We can use the API.home_timeline() method. This will return the 20 most recent tweets coming from
# friends and the user. This process will include three functions; get, write, and the actual retweet function.


# Retrieves the recent tweet from the text file. This is to recall the earliest tweet recorded
def get_recent_retweet():
    file_read = open('Last_seen_retweet.txt', 'r')
    latest_tweet_id = int(file_read.read().strip())
    file_read.close()
    return latest_tweet_id


# Stores a newly updated tweet received in the homepage, and store it into the text file.
def store_recent_retweet(latest_id):
    file_write = open('Last_seen_retweet.txt', 'w')
    file_write.write(str(latest_id))
    file_write.close()


# Retweets important events and emergencies that are happening around campus. These are limited to people
# I am following.
def retweet_tweets(listofusernames):
    print("Finding UT Austin related events to retweet and liking others...")
    recent_retweet = get_recent_retweet()
    all_tweets = api.home_timeline(since_id=recent_retweet, exclude_replies=True)
    # Words that will are strongly related to an event happening, will retweet if word is in sentence.
    words = ['event', 'celebrate', 'emergency', 'celebration',
             'join', 'opportunity', 'come', 'gather', 'connect',
             'present', 'sign', 'invite', 'alert', 'don\'t miss', 'apply']
    for current_tweet in reversed(all_tweets):
        # This if statement makes sure the tweet is from our following only, if not we continue to the
        # next iteration.
        print(current_tweet.user.screen_name)
        if not (current_tweet.user.screen_name in listofusernames):
            continue
        recent_tweet = current_tweet.id
        store_recent_retweet(recent_tweet)
        api.create_favorite(recent_tweet)
        current_tweet_text = current_tweet.text.lower()
        print("The current tweet is: '" + current_tweet_text + "'")
        check = False
        # Checks if the current tweet contains one of these variations of words
        for word in words:
            if word in current_tweet_text:
                check = True
                break
        respond_to_tweets(check, current_tweet, recent_tweet)


# Responds to tweet's that are showing in the home page and carries certain key-words.
def respond_to_tweets(check, current_tweet, recent_tweet):
    if check:
        print("Found Tweet!!!, currently retweeting and liking tweet..." + "\n")
        message = ' Very Cool!!!'
        # Auto_populate_to_reply mentions work together with in_reply_to_status_id to reply and update tweets
        api.update_status('@' + current_tweet.user.screen_name + message,
                          in_reply_to_status_id=recent_tweet, auto_populate_reply_metadata=True)
        api.retweet(recent_tweet)
        print("Tweet successfully retweeted!")
    else:
        print("tweet liked!")


# Main functions to run the program
def main():
    # Quick Info functions:
    # find_individual_info('UTAustin')
    listofusernames = follow_people("")
    # find_list_info()

    # Repetitive constant functions:
    while True:
        reply_to_mentions()
        print("")
        retweet_tweets(listofusernames)
        time.sleep(50)
        print("")


main()


# Functions that we could create:
# Info about a specific user, basically the layout about the user (optional,
# not really needed, but nice and quick info) (CHECK)
# Additional to the first function above, create one that loops through
# a list or map of users, similar to first. (CHECK)
# Create a txt file of UT associated accounts, then have a function read
# in that list and follow those people (CHECK)
# Create a txt file associated with two functions; a retrieve name and
# store name. This will make sure there aren't duplicates (CHECK)

# Things to do with twitterBot:
# Tweet to UT accounts, something supportive everytime they post something "CHECK"
# Retweet UT associated events or anything in general (CHECK)
# Do something when someone @'s this bot, this can be like a UT happy quote or something like that "CHECK"
# In addition to function on top, when someone @'s and # something specific like "event", "CHECK"
# we can retweet the post, and say that there is an event happening "CHECK"
