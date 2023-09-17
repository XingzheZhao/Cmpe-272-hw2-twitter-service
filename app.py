from flask import Flask, render_template, request, redirect, url_for, session
from requests_oauthlib import OAuth1Session
from twitter_service import TwitterAdsAPI
import configparser
import secrets

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
    global oauth
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )

    return redirect('/')

# Initialize TwitterAdsAPI with the authenticated user's credentials
# twitter_api = TwitterAdsAPI(consumer_key, consumer_secret, session['twitter_token'][0], session['twitter_token'][1])

#TODO modify create_tweet from twitter service
@app.route('/create_tweet', methods=['POST'])
def create_tweet():
    # text = request.form['tweet_text']
    # payload = {"text": text}
    # result = twitter_api.create_tweet(payload)
    return redirect(url_for('result', result=result))

#TODO modify delete_tweet from twitter service
@app.route('/delete_tweet', methods=['POST'])
def delete_tweet():
    # tweet_id = request.form['tweet_id']
    # result = twitter_api.delete_tweet(tweet_id)
    return redirect(url_for('result', result=result))

#TODO modify result from twitter service
@app.route('/result')
def result():
    # result = request.args.get('result')
    return render_template('result.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
