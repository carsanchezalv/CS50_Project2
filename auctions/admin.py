from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(AuctionsInfo)
admin.site.register(Bids)
admin.site.register(Comments)
admin.site.register(Watchlist)
admin.site.register(Winner)