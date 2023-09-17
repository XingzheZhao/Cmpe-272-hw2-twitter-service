import tweepy

class TwitterAdsAPI:
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(self.auth)

    def create_tweet(self, text):
        try:
            tweet = self.api.update_status(status=text)
            return f"Tweet created successfully with ID: {tweet.id}"
        except tweepy.errors.TweepyException as e:
            return f"Error creating tweet: {str(e)}"

    def delete_tweet(self, tweet_id):
        try:
            self.api.destroy_status(tweet_id)
            return f"Tweet with ID {tweet_id} deleted successfully"
        except tweepy.errors.TweepyException as e:
            return f"Error deleting tweet: {str(e)}"