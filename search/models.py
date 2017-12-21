from __future__ import unicode_literals
from django.db import models
from base64 import b16decode, b16encode


class UrlFile(models.Model):
    url = models.CharField(max_length=250, unique=True)
    text = models.TextField()

    def __str__(self):
        return b16decode(self.url)


class WordPosition(models.Model):
    word = models.CharField(max_length=100)
    url_file = models.ForeignKey(UrlFile)
    rank = models.FloatField(default=0.0)

    def __str__(self):
        return self.word
