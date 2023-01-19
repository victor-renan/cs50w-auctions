from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
# Register your models here.

admin.site.register(User, UserAdmin)
admin.site.register(Listings)
admin.site.register(Bids)
admin.site.register(Watchlists)
admin.site.register(Comments)
admin.site.register(Categories)