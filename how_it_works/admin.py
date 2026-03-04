from django.contrib import admin

from .models import (
    FAQ,
    BadgesHIW,
    GetStarted,
    MentalHIW,
    PhysicalHIW,
    PrizesHIW,
    SocialHIW,
)

admin.site.register(GetStarted)
admin.site.register(PhysicalHIW)
admin.site.register(MentalHIW)
admin.site.register(SocialHIW)
admin.site.register(PrizesHIW)
admin.site.register(BadgesHIW)
admin.site.register(FAQ)
