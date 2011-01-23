from django.db import models


class Region(models.Model):
    name = models.CharField(unique = True, max_length = 200)
    country = models.CharField(max_length = 2)


class Location(models.Model):
    region = models.ForeignKey(Region)


class Producer(models.Model):
    name   = models.CharField(unique = True, max_length = 200)
    location = models.ForeignKey(Location)
    
    
class Wine(models.Model):
    producer = models.ForeignKey(Producer, related_name = 'wines')
    
    
class Grape(models.Model):
    name = models.CharField(unique = True, max_length = 200)

    
class GrapeWine(models.Model):
    grape = models.ForeignKey(Grape, related_name = 'wines')
    wine  = models.ForeignKey(Wine, related_name = 'grapes')
    percentage = models.FloatField(default = 1)


