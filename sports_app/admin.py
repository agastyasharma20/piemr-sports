from django.contrib import admin
from django.utils.html import format_html
from .models import (
    StudentProfile, Team, Achievement, Opportunity, 
    StudentInterestForm, EventRegistration, Announcement
)

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'roll_number', 'branch', 'year', 'phone')
    list_filter = ('year', 'branch', 'created_at')
    search_fields = ('user__first_name', 'roll_number', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User Information', {'fields': ('user',)}),
        ('Student Details', {'fields': ('roll_number', 'branch', 'year', 'phone', 'profile_picture')}),
        ('Metadata', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def get_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_name.short_description = 'Name'


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'sport', 'coach_name', 'members_count', 'is_active', 'get_logo_preview')
    list_filter = ('sport', 'is_active', 'establishment_year')
    search_fields = ('name', 'coach_name', 'coach_email')
    readonly_fields = ('created_at', 'updated_at', 'get_logo_preview')
    fieldsets = (
        ('Team Information', {'fields': ('name', 'sport', 'description', 'team_logo', 'get_logo_preview')}),
        ('Coach Details', {'fields': ('coach_name', 'coach_email', 'coach_phone')}),
        ('Other Details', {'fields': ('members_count', 'establishment_year', 'is_active')}),
        ('Metadata', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def get_logo_preview(self, obj):
        if obj.team_logo:
            return format_html('<img src="{}" width="100" height="100" />', obj.team_logo.url)
        return "No logo"
    get_logo_preview.short_description = 'Logo Preview'


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'team', 'achievement_type', 'date', 'is_featured', 'get_image_preview')
    list_filter = ('achievement_type', 'team', 'date', 'is_featured')
    search_fields = ('title', 'player_names')
    readonly_fields = ('created_at', 'updated_at', 'get_image_preview')
    fieldsets = (
        ('Achievement Details', {'fields': ('title', 'description', 'team', 'achievement_type')}),
        ('Event Information', {'fields': ('date', 'location', 'player_names')}),
        ('Media', {'fields': ('image', 'get_image_preview', 'certificate_image')}),
        ('Display', {'fields': ('is_featured',)}),
        ('Metadata', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def get_image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="150" height="150" />', obj.image.url)
        return "No image"
    get_image_preview.short_description = 'Image Preview'


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'team', 'event_type', 'start_date', 'status', 'registration_deadline')
    list_filter = ('status', 'team', 'event_type', 'start_date')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Event Details', {'fields': ('title', 'description', 'team', 'event_type')}),
        ('Dates & Registration', {'fields': ('start_date', 'end_date', 'registration_deadline', 'max_participants')}),
        ('Location & Details', {'fields': ('location', 'eligibility_criteria', 'poster_image')}),
        ('Contact Information', {'fields': ('contact_person', 'contact_email', 'contact_phone')}),
        ('Status', {'fields': ('status',)}),
        ('Metadata', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    date_hierarchy = 'start_date'


@admin.register(StudentInterestForm)
class StudentInterestFormAdmin(admin.ModelAdmin):
    list_display = ('name', 'roll_number', 'year', 'branch', 'submission_date', 'is_reviewed')
    list_filter = ('year', 'branch', 'submission_date', 'is_reviewed')
    search_fields = ('name', 'roll_number', 'email')
    readonly_fields = ('user', 'submission_date', 'roll_number', 'name', 'email', 'phone', 'branch', 'year')
    fieldsets = (
        ('Student Information', {'fields': ('user', 'roll_number', 'name', 'email', 'phone', 'branch', 'year')}),
        ('Sports Interest', {'fields': ('sports_interests', 'experience_level')}),
        ('Background', {'fields': ('past_achievements', 'additional_comments')}),
        ('Review Status', {'fields': ('is_reviewed',)}),
        ('Metadata', {'fields': ('submission_date',)}),
    )

    def has_add_permission(self, request):
        return False  # Only students can add, not admin


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('get_student_name', 'opportunity', 'registration_date', 'status')
    list_filter = ('status', 'opportunity', 'registration_date')
    search_fields = ('user__first_name', 'team_name')
    readonly_fields = ('user', 'opportunity', 'registration_date')
    fieldsets = (
        ('Registration Details', {'fields': ('user', 'opportunity', 'registration_date')}),
        ('Team Information', {'fields': ('team_name', 'team_members', 'contact_number')}),
        ('Status', {'fields': ('status', 'confirmation_date')}),
        ('Additional Notes', {'fields': ('notes',)}),
    )

    def get_student_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_student_name.short_description = 'Student Name'

    def has_add_permission(self, request):
        return False  # Only students can register
    
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'is_active', 'created_at', 'expires_at')
    list_filter = ('priority', 'is_active')
    search_fields = ('title', 'message')
    list_editable = ('is_active',)
    