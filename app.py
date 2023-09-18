from flask import Flask, render_template, request, redirect
from requests_oauthlib import OAuth1Session
import configparser
import secrets
import json

# References for authorization, create/delete tweets form Twitter Sample Code
# SEE: https://github.com/twitterdev/Twitter-API-v2-sample-code/blob/main/Manage-Tweets/create_tweet.py
# SEE: https://github.com/twitterdev/Twitter-API-v2-sample-code/blob/main/Manage-Tweets/delete_tweet.py


# Outline: Completed by: Peizu Li

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)

# Read the keys from config.ini file
# Add your own key in config.ini file
config = configparser.ConfigParser()
config.read('config.ini')
consumer_key = config['twitter']['CONSUMER_KEY']
consumer_secret = config['twitter']['CONSUMER_SECRET']

global twitter_api, flag
flag = True

# Get request token
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

# Authorization Link
authorization_url = oauth.authorization_url(base_authorization_url)

ask_redirection = "Please go here and authorise"

# Default Route: Completed by: Peizu Li
# This function call /templates/index.html, and the page will display differently based on the authorization condition
# return: call the templates/index.html with corresponding details
@app.route('/')
def index():
    if flag:
        return render_template('index.html', ask_redir=ask_redirection, url=authorization_url, condition=True)
    else:
        return render_template('index.html', condition=False) 

# Get PIN Route: Completed by: Peizu Li
# This function ask user to give access to the account
# return: redirect to /
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

    # Generate token and secret
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

    # back to home page
    return redirect('/')

# Create Tweet Function: Completed by: Sam Zhao
# This function receive user input on tweet creation, and write a tweet for the user
# return: redirect to template/result.html page with corresponding information based on status
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
        return render_template('result.html', task_type=task_type, condition=False, err=error_detail)
    else:
        id = json.dumps(json_response['data']['id'])
        tweet = json.dumps(json_response['data']['text'])
        return render_template('result.html', task_type=task_type, condition=True, id=id, tweet=tweet)

# Delete Tweet Function: Completed by: 
# This function receive user input as tweet id, and delete the corresponding tweet
# return: redirect to template/result.html page with corresponding information based on status
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

# Result Route: Completed by: 
# This function called the /templates/result.html page
@app.route('/result')
def result():
    return render_template('result.html', task_type="none")

if __name__ == '__main__':
    app.run(debug=True)
