from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from requests_oauthlib import OAuth1Session
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
# References for authorization, create/delete tweets form Twitter Sample Code
# SEE: https://github.com/twitterdev/Twitter-API-v2-sample-code/blob/main/Manage-Tweets/create_tweet.py
# SEE: https://github.com/twitterdev/Twitter-API-v2-sample-code/blob/main/Manage-Tweets/delete_tweet.py
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

# Based urls
base_authorization_url = "https://api.twitter.com/oauth/authorize"
access_token_url = "https://api.twitter.com/oauth/access_token"

authorization_url = oauth.authorization_url(base_authorization_url)

ask_redirection = "Please go here and authorise"

@app.route('/')
def index():
    if flag:
        return render_template('index.html', ask_redir=ask_redirection, url=authorization_url, condition=True)
    else:
        return render_template('index.html', condition=False) 

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

@app.route('/create_tweet', methods=['POST'])
def create_tweet():
    text = request.form['tweet_text']
    payload = {"text": text}
    response = oauth.post(
        "https://api.twitter.com/2/tweets",
        json=payload,
    )
    json_response = response.json()
    task_type = "create"
    if response.status_code != 201:
        json_response = response.json() 
        error_detail = json_response['detail']
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        return render_template('result.html', task_type=task_type, condition=False, time=current_time, err=error_detail)
    else:
        id = json.dumps(json_response['data']['id'])
        tweet = json.dumps(json_response['data']['text'])
        return render_template('result.html', task_type=task_type, condition=True, id=id, tweet=tweet)

@app.route('/delete_tweet', methods=['POST'])
def delete_tweet():
    tweet_id = request.form['tweet_id']
    response = oauth.delete(f"https://api.twitter.com/2/tweets/{tweet_id}")

    task_type = "delete"
    if response.status_code != 200:
        json_response = response.json() 
        error_detail = json_response['detail']
        return render_template('result.html', task_type=task_type, condition=False, err=error_detail)
    else:
        return render_template('result.html', task_type=task_type, condition=True, tweet_id=tweet_id)

@app.route('/result')
def result():
    return render_template('result.html', task_type="none")

if __name__ == '__main__':
    app.run(debug=True)
