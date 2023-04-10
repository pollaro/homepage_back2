from django.db import models


class HBLManager(models.Model):
    hbl_id = models.IntegerField()
    name = models.CharField(max_length=64)
    email = models.EmailField(max_length=100, null=True)
    guid = models.CharField(max_length=64, default=None, null=True)
