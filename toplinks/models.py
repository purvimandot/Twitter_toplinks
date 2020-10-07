from django.db import models

# Databse Models for the app

class TwitterUser(models.Model):
    screen_name= models.CharField(max_length=100)
    twitter_url= models.URLField(max_length=200)
    user=models.CharField(blank=False, max_length=20)
    def __str__(self):
        return self.screen_name


class Tweet(models.Model):
    text= models.TextField()
    created_time= models.DateTimeField(auto_now=False, auto_now_add=False)
    tweet_id= models.BigIntegerField(blank=False)
    user=models.CharField(blank=False, max_length=20)
    def __str__(self):
        return self.text

