from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class AuctionsInfo(models.Model):
    user = models.CharField(max_length=64)
    title = models.CharField(max_length=64)
    desc = models.TextField()       
    starting_bid = models.IntegerField()        
    image_url = models.CharField(max_length=228, default = None, blank = True, null = True)
    category = models.CharField(max_length = 64)
    active_bool = models.BooleanField(default = True)

class Bids(models.Model):
    user = models.CharField(max_length=30)
    listingid = models.IntegerField()
    bid = models.IntegerField()
    
class Comments(models.Model):
    user = models.CharField(max_length=64)
    comment = models.TextField()
    listingid = models.IntegerField()

class Watchlist(models.Model):
    watch_list = models.ForeignKey(AuctionsInfo, on_delete=models.CASCADE)
    user = models.CharField(max_length=64)

class Winner(models.Model):
    bid_win_list = models.ForeignKey(AuctionsInfo, on_delete = models.CASCADE)
    user = models.CharField(max_length=64, default = None)