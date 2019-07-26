from django.contrib import admin

# Register your models here.
from .models import *

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    ordering = ('name',)
    search_fields = ('name', 'slug')

@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    readonly_fields = ('teams', 'tournament')
    ordering = ('name',)
    search_fields = ('name', 'slug')

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('division', 'phase', 'name')
    readonly_fields = ('division','phase','referee_group')
    ordering = ('division', 'phase', 'name')
    search_fields = ('name', 'division')

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    search_fields = ('name',)

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'division', 'group', 'phase_block', 'home', 'away', 'referee')
    readonly_fields = ('division', 'group', 'phase_block', 'home', 'away')
    ordering = ('division', 'group', 'phase_block')
    search_fields = ('home', 'away', 'referee')
