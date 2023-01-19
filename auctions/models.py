from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    pass


class Listings(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    posting_date = models.DateField(auto_now=True)
    title = models.CharField(max_length=128)
    card_description = models.CharField(max_length=320)
    description = models.TextField()
    starting_bid = models.FloatField()
    image_url = models.CharField(max_length=600)
    category = models.ForeignKey('Categories', on_delete=models.SET_NULL, null=True)
    status = models.BooleanField(default=True)
    winner_bid = models.ForeignKey('Bids', on_delete=models.CASCADE, default=None, blank=True)

    def __str__(self):
        return f"{self.title}"


class Comments(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    listing = models.ForeignKey('Listings', on_delete=models.CASCADE)
    comment = models.TextField(max_length=600)
    date = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.user} in {self.listing}"


class Bids(models.Model):
    date = models.DateField(auto_now=True)
    listing = models.ForeignKey('Listings', on_delete=models.CASCADE, default=None)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    value = models.FloatField()

    def __str__(self):
        return f"{self.user}: {self.value}"


class Categories(models.Model):
    name = models.CharField(max_length=120)

    def __str__(self):
        return f"{self.name}"


class Watchlists(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    listing = models.ForeignKey('Listings', on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)

