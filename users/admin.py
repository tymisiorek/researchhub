# admin.py
from django.contrib import admin
from .models import Profile  # or from .models import User if using custom user model
from project_b_07.models import TeamFile

admin.site.register(Profile)  # or admin.site.register(User)

@admin.register(TeamFile)
class TeamFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'file', 'description', 'keywords')