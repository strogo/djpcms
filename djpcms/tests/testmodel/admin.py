from django.contrib import admin
from djpcms.tests.testmodel.models import Strategy, StrategyTrade

class StrategyTradeAdmin(admin.TabularInline):
    model = StrategyTrade
    
class StrategyAdmin(admin.ModelAdmin):
    inlines  = [StrategyTradeAdmin]
    
admin.site.register(Strategy, StrategyAdmin)