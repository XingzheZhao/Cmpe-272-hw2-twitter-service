import unittest
from app import app, oauth
import json

# Unit Test Class with Functions: Completed by Sam Zhao
# This class with two unit test function below checks the connection when user enter a tweet and click post, and when user enter a tweet id then press delete.
class TestApp(unittest.TestCase):
    def test_create_tweet(self):
        # for successfully create a tweet
        with app.test_client() as client:
            testing_tweet = {"tweet_text": "this is a testing tweet"}
            # test 1 - checking connection
            res = client.post('/create_tweet', data=testing_tweet)
            self.assertEqual(res.status_code, 200)


    def test_delete_tweet(self):
        with app.test_client() as client:
            testing_tweet_id = {"tweet_id": "1703567972739285066"}
            res = client.post('/delete_tweet', data=testing_tweet_id)
            self.assertEqual(res.status_code, 200)



if __name__ == "__main__":
    unittest.main()