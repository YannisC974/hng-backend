from django.contrib import admin

from prizes.models import Badge, DailyPrize, Medal

admin.site.register(DailyPrize)
admin.site.register(Medal)
admin.site.register(Badge)
