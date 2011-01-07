from django.db import models


class Strategy(models.Model):
    name     = models.CharField(unique = True, max_length = 200)
    description = models.TextField(blank = True)
    
    def __unicode__(self):
        return u'%s' % self.name
    
    
class Trade(models.Model):
    name = models.CharField(unique = True, max_length = 200)
    currency = models.CharField(max_length = 3, help_text="trade currency")
    
    
class StrategyTrade(models.Model):
    strategy   = models.ForeignKey(Strategy, related_name = 'wines')
    trade      = models.ForeignKey(Trade, related_name = 'grapes')
    percentage = models.FloatField(default = 1)