from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout, login
from toplinks.models import Tweet, TwitterUser
import tweepy
import tldextract
import datetime

consumer_key='ntRWC8TgucrSgJBFhFTDFLrlp'
consumer_secret='6i0gOsO55zZjSOI44eMTXvyZiD881Xr6cLDtrOYZUe1btcmnpi'

# Homepage
@login_required(login_url="/login")
def home(request):
    #Authenticating with Twitter

    user=User.objects.get(username= request.user.username)
    #print(user)
    social=user.social_auth.get(provider='twitter')

    #Generating access tokens
    access_token=social.extra_data['access_token']
    access_key= access_token["oauth_token"]
    access_secret= access_token["oauth_token_secret"]
    
    #Using Tweepy OAuthHandler
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth,wait_on_rate_limit=True)
    startDate = datetime.datetime.now() - datetime.timedelta(days=7)
    
    #Extracting tweets from Tweepy
    tweets = tweepy.Cursor(api.home_timeline,
                        tweet_mode="extended",
                        lang="en").items(20)

    #Saving in the database
    for tweet in tweets:
        if tweet.created_at>startDate:
            if tweet.entities["urls"]:
                
                sn=tweet.user.screen_name
                if not len(Tweet.objects.filter(tweet_id=tweet.id)):
                    t=Tweet(text= tweet.full_text,created_time=tweet.created_at,tweet_id=tweet.id,user=request.user.username)
                    t.save()
                    for u in tweet.entities["urls"]:
                        tu= TwitterUser(screen_name = sn,twitter_url = u["expanded_url"],user=request.user.username)
                        tu.save()               
        else:
            break
    
    tweets=[]
    screen_names={}
    dom={}
    a=[]
    # Extracting tweets with text and ID
    tweet_query=Tweet.objects.filter(user= request.user.username)
    for i in tweet_query:
        if i.created_time.replace(tzinfo=None)>startDate.replace(tzinfo=None):
            tweets.append([i.text,i.tweet_id])

    twitter_user_query= TwitterUser.objects.filter(user= request.user.username)

    #Extracting names of users who shared tweets with URL's
    for j in twitter_user_query:
        if j not in screen_names:
            screen_names[j]=1
        else:
            screen_names[j]+=1
        info = tldextract.extract(j.twitter_url)

        #Making dictionary of domain name
        if info.registered_domain not in dom:
            dom[info.registered_domain]=1
        else:
            dom[info.registered_domain]+=1 

        # Users who shared most tweets
    m=0
    for k,v in screen_names.items():
        if v>m:
            m=v
            a.append(k)

    return render(request,'home.html',{"tweets":tweets,"a":a,"dom":dom})

#LoginPage
def loginPage(request):
    if not request.user.is_authenticated:
        return render(request,'login.html')
    else:
        return redirect('/')

#Redirecting to homepage after logout
def logoutPage(request):
    logout(request)
    return redirect('/login')