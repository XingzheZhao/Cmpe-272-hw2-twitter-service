from flask import Flask, render_template, request, redirect, url_for, session
from requests_oauthlib import OAuth1Session
from twitter_service import TwitterAdsAPI
import configparser
import secrets
import json

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)

config = configparser.ConfigParser()
config.read('config.ini')
consumer_key = config['twitter']['CONSUMER_KEY']
consumer_secret = config['twitter']['CONSUMER_SECRET']

global twitter_api, flag
flag = True

# Get request token
# References: 
request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

try:
    fetch_response = oauth.fetch_request_token(request_token_url)
except ValueError:
    print(
        "There may have been an issue with the consumer_key or consumer_secret you entered."
    )

resource_owner_key = fetch_response.get("oauth_token")
resource_owner_secret = fetch_response.get("oauth_token_secret")
print("Got OAuth token: %s" % resource_owner_key)

# Based urls
base_authorization_url = "https://api.twitter.com/oauth/authorize"
access_token_url = "https://api.twitter.com/oauth/access_token"


authorization_url = oauth.authorization_url(base_authorization_url)

ask_redirection = "Please go here and authorise %s" % authorization_url

@app.route('/')
def index():
    print(flag)
    if flag:
        return render_template('index.html', ask_redir=ask_redirection, condition=True)
    else:
        return render_template('index.html', ask_redir=None, condition=False) 

@app.route('/get_pin', methods=['POST'])
def get_pin():
    global oauth
    verifier = request.form['pin_number']

    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier,
    )
    oauth_tokens = oauth.fetch_access_token(access_token_url)

    access_token = oauth_tokens["oauth_token"]
    access_token_secret = oauth_tokens["oauth_token_secret"]
    global flag
    flag = False

    # Make the request
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )

    return redirect('/')

# Initialize TwitterAdsAPI with the authenticated user's credentials
# twitter_api = TwitterAdsAPI(consumer_key, consumer_secret, session['twitter_token'][0], session['twitter_token'][1])

# Create Tweet
@app.route('/create_tweet', methods=['POST'])
def create_tweet():
    text = request.form['tweet_text']
    payload = {"text": text}
    response = oauth.post(
        "https://api.twitter.com/2/tweets",
        json=payload,
    )
    json_response = response.json()

    if response.status_code != 201:
        result = f"Error"
        return render_template('result.html', condition=False, cflag=True, result=result)
    else:
        id = json.dumps(json_response['data']['id'])
        tweet = json.dumps(json_response['data']['text'])
        return render_template('result.html', condition=True, cflag=True, id=id, tweet=tweet)

# Delete Tweet
@app.route('/delete_tweet', methods=['POST'])
def delete_tweet():
    tweet_id = request.form['tweet_id']
    response = oauth.delete("https://api.twitter.com/2/tweets/{}".format(tweet_id))

    json_response = response.json()

    if response.status_code != 200:
        result = f"Error"
        return render_template('result.html', condition=False, cflag=False, result=result)
    else:
        return render_template('result.html', condition=True, cflag=False)


#TODO modify result from twitter service
@app.route('/result')
def result():
    return render_template('result.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
