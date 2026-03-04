from django.contrib import admin

from .models import (
    Challenge,
    Instructor,
    IntensePhysicalChallenge,
    MentalChallenge,
    ModeratePhysicalChallenge,
    SocialChallenge,
)

admin.site.register(Challenge)
admin.site.register(ModeratePhysicalChallenge)
admin.site.register(IntensePhysicalChallenge)
admin.site.register(MentalChallenge)
admin.site.register(SocialChallenge)
admin.site.register(Instructor)
