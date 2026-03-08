from django.contrib import admin
from django.utils.html import format_html
from .models import (
    StudentProfile, Team, TeamMember, Achievement, Opportunity,
    StudentInterestForm, EventRegistration, Announcement,
    GalleryPhoto, Badge, Certificate, LeaderboardEntry
)


# ─── STUDENT PROFILE ──────────────────────────────────────────────────────────

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        'get_name', 'roll_number', 'branch', 'year',
        'phone', 'experience_level', 'onboarding_complete', 'get_avatar'
    )
    list_filter = ('year', 'branch', 'experience_level', 'onboarding_complete', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'roll_number', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'get_avatar')
    fieldsets = (
        ('User Account', {
            'fields': ('user', 'get_avatar', 'profile_picture')
        }),
        ('Basic Info — Step 1', {
            'fields': ('roll_number', 'branch', 'year', 'phone', 'date_of_birth', 'gender')
        }),
        ('Sports History — Step 2', {
            'fields': ('past_achievements', 'experience_level', 'years_playing', 'highest_level', 'certificates'),
            'classes': ('collapse',)
        }),
        ('Sports Interests — Step 3', {
            'fields': ('sports_interests', 'position_played', 'availability', 'willing_to_travel'),
            'classes': ('collapse',)
        }),
        ('Physical Details — Step 4', {
            'fields': ('height_cm', 'weight_kg', 'fitness_level', 'medical_conditions'),
            'classes': ('collapse',)
        }),
        ('Onboarding & Verification', {
            'fields': ('onboarding_step', 'onboarding_complete', 'email_verified', 'email_token'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_name.short_description = 'Name'

    def get_avatar(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="60" height="60" style="border-radius:12px;object-fit:cover;" />',
                obj.profile_picture.url
            )
        initials = (obj.user.first_name[:1] + obj.user.last_name[:1]).upper() or obj.user.username[:2].upper()
        return format_html(
            '<div style="width:60px;height:60px;border-radius:12px;background:linear-gradient(135deg,#1a3c6e,#2563a8);display:flex;align-items:center;justify-content:center;color:white;font-weight:900;font-size:1.2rem;">{}</div>',
            initials
        )
    get_avatar.short_description = 'Photo'


# ─── TEAM ─────────────────────────────────────────────────────────────────────

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = (
        'get_logo_preview', 'name', 'sport', 'coach_name',
        'members_count', 'wins', 'tournaments_played', 'is_active'
    )
    list_filter = ('sport', 'is_active', 'establishment_year')
    search_fields = ('name', 'coach_name', 'coach_email')
    readonly_fields = ('created_at', 'updated_at', 'get_logo_preview', 'get_coach_photo_preview')
    list_editable = ('is_active',)
    fieldsets = (
        ('Team Information', {
            'fields': ('name', 'sport', 'description', 'team_logo', 'get_logo_preview', 'is_active')
        }),
        ('Coach Details', {
            'fields': ('coach_name', 'coach_email', 'coach_phone', 'coach_photo', 'get_coach_photo_preview', 'coach_bio')
        }),
        ('Stats & Info', {
            'fields': ('members_count', 'establishment_year', 'wins', 'tournaments_played')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_logo_preview(self, obj):
        if obj.team_logo:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius:10px;object-fit:cover;" />',
                obj.team_logo.url
            )
        sport_emojis = {
            'cricket': '🏏', 'football': '⚽', 'basketball': '🏀',
            'volleyball': '🏐', 'badminton': '🏸', 'table_tennis': '🏓',
            'athletics': '🏃', 'swimming': '🏊', 'other': '🏅'
        }
        emoji = sport_emojis.get(obj.sport, '🏅')
        return format_html(
            '<div style="width:50px;height:50px;border-radius:10px;background:#f0f4f8;display:flex;align-items:center;justify-content:center;font-size:1.5rem;">{}</div>',
            emoji
        )
    get_logo_preview.short_description = 'Logo'

    def get_coach_photo_preview(self, obj):
        if obj.coach_photo:
            return format_html(
                '<img src="{}" width="80" height="80" style="border-radius:12px;object-fit:cover;" />',
                obj.coach_photo.url
            )
        return 'No photo uploaded'
    get_coach_photo_preview.short_description = 'Coach Photo Preview'


# ─── TEAM MEMBER ──────────────────────────────────────────────────────────────

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = (
        'get_photo', 'name', 'team', 'role',
        'position', 'jersey_number', 'branch', 'year', 'is_active'
    )
    list_filter = ('team', 'role', 'is_active', 'year')
    search_fields = ('name', 'roll_number', 'position')
    list_editable = ('is_active',)
    fieldsets = (
        ('Member Info', {
            'fields': ('team', 'user', 'name', 'roll_number', 'photo')
        }),
        ('Role & Position', {
            'fields': ('role', 'position', 'jersey_number')
        }),
        ('Academic Info', {
            'fields': ('year', 'branch')
        }),
        ('Status', {
            'fields': ('is_active', 'joined_date')
        }),
    )

    def get_photo(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="45" height="45" style="border-radius:10px;object-fit:cover;" />',
                obj.photo.url
            )
        return format_html(
            '<div style="width:45px;height:45px;border-radius:10px;background:linear-gradient(135deg,#1a3c6e,#2563a8);display:flex;align-items:center;justify-content:center;color:white;font-weight:900;">{}</div>',
            obj.name[:1].upper()
        )
    get_photo.short_description = 'Photo'


# ─── ACHIEVEMENT ──────────────────────────────────────────────────────────────

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = (
        'get_image_preview', 'title', 'team',
        'achievement_type', 'date', 'location', 'is_featured'
    )
    list_filter = ('achievement_type', 'team', 'date', 'is_featured')
    search_fields = ('title', 'player_names', 'location')
    readonly_fields = ('created_at', 'updated_at', 'get_image_preview')
    list_editable = ('is_featured',)
    fieldsets = (
        ('Achievement Details', {
            'fields': ('title', 'description', 'team', 'achievement_type', 'is_featured')
        }),
        ('Event Information', {
            'fields': ('date', 'location', 'player_names')
        }),
        ('Media', {
            'fields': ('image', 'get_image_preview', 'certificate_image')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'date'

    def get_image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="120" height="80" style="border-radius:10px;object-fit:cover;" />',
                obj.image.url
            )
        return 'No image uploaded'
    get_image_preview.short_description = 'Image Preview'


# ─── OPPORTUNITY ──────────────────────────────────────────────────────────────

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'team', 'event_type',
        'start_date', 'status', 'registration_deadline',
        'get_registrations_count', 'max_participants'
    )
    list_filter = ('status', 'team', 'event_type', 'start_date')
    search_fields = ('title', 'description', 'location')
    readonly_fields = ('created_at', 'updated_at', 'get_registrations_count', 'get_poster_preview')
    list_editable = ('status',)
    fieldsets = (
        ('Event Details', {
            'fields': ('title', 'description', 'team', 'event_type', 'status')
        }),
        ('Dates & Registration', {
            'fields': ('start_date', 'end_date', 'registration_deadline', 'max_participants')
        }),
        ('Location & Eligibility', {
            'fields': ('location', 'eligibility_criteria')
        }),
        ('Poster', {
            'fields': ('poster_image', 'get_poster_preview')
        }),
        ('Contact Information', {
            'fields': ('contact_person', 'contact_email', 'contact_phone')
        }),
        ('Stats', {
            'fields': ('get_registrations_count',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'start_date'

    def get_registrations_count(self, obj):
        count = obj.registrations.count()
        color = '#22c55e' if obj.max_participants and count < obj.max_participants else '#ef4444'
        return format_html(
            '<span style="background:rgba(26,60,110,0.1);color:{};padding:3px 10px;border-radius:20px;font-weight:700;">{} registered</span>',
            color, count
        )
    get_registrations_count.short_description = 'Registrations'

    def get_poster_preview(self, obj):
        if obj.poster_image:
            return format_html(
                '<img src="{}" width="200" style="border-radius:10px;" />',
                obj.poster_image.url
            )
        return 'No poster uploaded'
    get_poster_preview.short_description = 'Poster Preview'


# ─── GALLERY PHOTO ────────────────────────────────────────────────────────────

@admin.register(GalleryPhoto)
class GalleryPhotoAdmin(admin.ModelAdmin):
    list_display = (
        'get_photo_preview', 'title', 'team',
        'category', 'taken_date', 'is_featured', 'uploaded_by'
    )
    list_filter = ('category', 'team', 'is_featured')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'get_photo_preview')
    list_editable = ('is_featured',)
    fieldsets = (
        ('Photo Info', {
            'fields': ('title', 'photo', 'get_photo_preview', 'description')
        }),
        ('Classification', {
            'fields': ('team', 'category', 'taken_date', 'is_featured')
        }),
        ('Metadata', {
            'fields': ('uploaded_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def get_photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="120" height="80" style="border-radius:10px;object-fit:cover;" />',
                obj.photo.url
            )
        return 'No photo'
    get_photo_preview.short_description = 'Preview'

    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


# ─── BADGE ────────────────────────────────────────────────────────────────────

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = (
        'get_badge_icon', 'user', 'badge_type',
        'title', 'sport', 'awarded_by', 'awarded_date'
    )
    list_filter = ('badge_type', 'sport', 'awarded_date')
    search_fields = ('user__first_name', 'user__last_name', 'user__username', 'title')
    readonly_fields = ('awarded_date',)
    fieldsets = (
        ('Badge Details', {
            'fields': ('user', 'badge_type', 'title', 'description', 'sport')
        }),
        ('Award Info', {
            'fields': ('awarded_by', 'event', 'awarded_date')
        }),
    )

    def get_badge_icon(self, obj):
        icons = {
            'gold': '🥇', 'silver': '🥈', 'bronze': '🥉',
            'excellence': '⭐', 'leadership': '👑', 'participation': '🏅'
        }
        colors = {
            'gold': '#f0a500', 'silver': '#9ca3af', 'bronze': '#b4783c',
            'excellence': '#8b5cf6', 'leadership': '#1a3c6e', 'participation': '#22c55e'
        }
        icon = icons.get(obj.badge_type, '🏅')
        color = colors.get(obj.badge_type, '#6c757d')
        return format_html(
            '<div style="width:40px;height:40px;border-radius:10px;background:{};display:flex;align-items:center;justify-content:center;font-size:1.3rem;opacity:0.85;">{}</div>',
            color + '20', icon
        )
    get_badge_icon.short_description = 'Badge'


# ─── CERTIFICATE ──────────────────────────────────────────────────────────────

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = (
        'get_cert_icon', 'user', 'title',
        'certificate_id', 'event', 'issued_date', 'is_valid'
    )
    list_filter = ('is_valid', 'issued_date')
    search_fields = ('user__username', 'user__first_name', 'certificate_id', 'title')
    readonly_fields = ('issued_date', 'certificate_id')
    list_editable = ('is_valid',)
    fieldsets = (
        ('Certificate Info', {
            'fields': ('user', 'title', 'event')
        }),
        ('Verification', {
            'fields': ('certificate_id', 'is_valid', 'issued_date')
        }),
    )

    def get_cert_icon(self, obj):
        color = '#22c55e' if obj.is_valid else '#ef4444'
        return format_html(
            '<span style="font-size:1.3rem;">📜</span>'
            '<span style="margin-left:6px;font-size:0.7rem;font-weight:700;color:{};">{}</span>',
            color, 'Valid' if obj.is_valid else 'Invalid'
        )
    get_cert_icon.short_description = 'Status'


# ─── LEADERBOARD ──────────────────────────────────────────────────────────────

@admin.register(LeaderboardEntry)
class LeaderboardEntryAdmin(admin.ModelAdmin):
    list_display = (
        'get_rank_badge', 'user', 'sport',
        'points', 'events_participated', 'medals', 'updated_at'
    )
    list_filter = ('sport',)
    search_fields = ('user__first_name', 'user__last_name', 'user__username')
    readonly_fields = ('updated_at',)
    ordering = ('-points',)
    fieldsets = (
        ('Student', {
            'fields': ('user', 'sport')
        }),
        ('Stats', {
            'fields': ('points', 'events_participated', 'medals', 'rank')
        }),
        ('Metadata', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )

    def get_rank_badge(self, obj):
        all_entries = LeaderboardEntry.objects.filter(sport=obj.sport).order_by('-points')
        rank = list(all_entries.values_list('id', flat=True)).index(obj.id) + 1 if obj.id in list(all_entries.values_list('id', flat=True)) else '—'
        if rank == 1:
            return format_html('<span style="font-size:1.2rem;">🥇</span>')
        elif rank == 2:
            return format_html('<span style="font-size:1.2rem;">🥈</span>')
        elif rank == 3:
            return format_html('<span style="font-size:1.2rem;">🥉</span>')
        return format_html(
            '<span style="background:#f0f4f8;color:#6c757d;padding:3px 8px;border-radius:8px;font-weight:700;font-size:0.78rem;">#{}</span>',
            rank
        )
    get_rank_badge.short_description = 'Rank'


# ─── STUDENT INTEREST FORM ────────────────────────────────────────────────────

@admin.register(StudentInterestForm)
class StudentInterestFormAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'roll_number', 'year', 'branch',
        'experience_level', 'submission_date', 'get_review_status'
    )
    list_filter = ('year', 'branch', 'experience_level', 'submission_date', 'is_reviewed')
    search_fields = ('name', 'roll_number', 'email')
    readonly_fields = (
        'user', 'submission_date', 'roll_number',
        'name', 'email', 'phone', 'branch', 'year'
    )
    list_editable = ('is_reviewed',) if False else ()  # Use action instead
    actions = ['mark_as_reviewed', 'mark_as_pending']
    fieldsets = (
        ('Student Information', {
            'fields': ('user', 'roll_number', 'name', 'email', 'phone', 'branch', 'year')
        }),
        ('Sports Interest', {
            'fields': ('sports_interests', 'experience_level')
        }),
        ('Background', {
            'fields': ('past_achievements', 'additional_comments')
        }),
        ('Review Status', {
            'fields': ('is_reviewed',)
        }),
        ('Metadata', {
            'fields': ('submission_date',)
        }),
    )

    def has_add_permission(self, request):
        return False

    def get_review_status(self, obj):
        if obj.is_reviewed:
            return format_html(
                '<span style="background:rgba(34,197,94,0.1);color:#166534;padding:3px 12px;border-radius:20px;font-weight:700;font-size:0.78rem;">✓ Reviewed</span>'
            )
        return format_html(
            '<span style="background:rgba(240,165,0,0.1);color:#92400e;padding:3px 12px;border-radius:20px;font-weight:700;font-size:0.78rem;">⏳ Pending</span>'
        )
    get_review_status.short_description = 'Status'

    @admin.action(description='Mark selected forms as Reviewed')
    def mark_as_reviewed(self, request, queryset):
        updated = queryset.update(is_reviewed=True)
        self.message_user(request, f'{updated} form(s) marked as reviewed.')

    @admin.action(description='Mark selected forms as Pending')
    def mark_as_pending(self, request, queryset):
        updated = queryset.update(is_reviewed=False)
        self.message_user(request, f'{updated} form(s) marked as pending.')


# ─── EVENT REGISTRATION ───────────────────────────────────────────────────────

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = (
        'get_student_name', 'opportunity', 'get_sport',
        'registration_date', 'get_status_badge', 'contact_number'
    )
    list_filter = ('status', 'opportunity', 'registration_date')
    search_fields = ('user__first_name', 'user__last_name', 'team_name', 'contact_number')
    readonly_fields = ('user', 'opportunity', 'registration_date')
    actions = ['confirm_registrations', 'mark_participated', 'cancel_registrations']
    fieldsets = (
        ('Registration Details', {
            'fields': ('user', 'opportunity', 'registration_date')
        }),
        ('Team Information', {
            'fields': ('team_name', 'team_members', 'contact_number')
        }),
        ('Status', {
            'fields': ('status', 'confirmation_date')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return False

    def get_student_name(self, obj):
        name = obj.user.get_full_name() or obj.user.username
        try:
            roll = obj.user.student_profile.roll_number or ''
            return format_html(
                '<strong>{}</strong><br><small style="color:#6c757d;">{}</small>',
                name, roll
            )
        except Exception:
            return name
    get_student_name.short_description = 'Student'

    def get_sport(self, obj):
        return obj.opportunity.team.get_sport_display()
    get_sport.short_description = 'Sport'

    def get_status_badge(self, obj):
        colors = {
            'registered': ('#1a3c6e', 'rgba(26,60,110,0.1)'),
            'confirmed': ('#166534', 'rgba(34,197,94,0.1)'),
            'participated': ('#92400e', 'rgba(240,165,0,0.1)'),
            'cancelled': ('#991b1b', 'rgba(239,68,68,0.1)'),
        }
        text_color, bg_color = colors.get(obj.status, ('#6c757d', '#f0f4f8'))
        return format_html(
            '<span style="background:{};color:{};padding:3px 12px;border-radius:20px;font-weight:700;font-size:0.78rem;">{}</span>',
            bg_color, text_color, obj.get_status_display()
        )
    get_status_badge.short_description = 'Status'

    @admin.action(description='Confirm selected registrations')
    def confirm_registrations(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='confirmed', confirmation_date=timezone.now())
        self.message_user(request, f'{updated} registration(s) confirmed.')

    @admin.action(description='Mark selected as Participated')
    def mark_participated(self, request, queryset):
        updated = queryset.update(status='participated')
        self.message_user(request, f'{updated} registration(s) marked as participated.')

    @admin.action(description='Cancel selected registrations')
    def cancel_registrations(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} registration(s) cancelled.')


# ─── ANNOUNCEMENT ─────────────────────────────────────────────────────────────

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        'get_priority_badge', 'title',
        'get_active_status', 'created_at', 'expires_at'
    )
    list_filter = ('priority', 'is_active')
    search_fields = ('title', 'message')
    list_editable = ('is_active',) if False else ()
    actions = ['activate_announcements', 'deactivate_announcements']
    fieldsets = (
        ('Announcement', {
            'fields': ('title', 'message', 'priority')
        }),
        ('Visibility', {
            'fields': ('is_active', 'expires_at')
        }),
    )

    def get_priority_badge(self, obj):
        colors = {
            'low': ('#166534', 'rgba(34,197,94,0.1)'),
            'medium': ('#92400e', 'rgba(240,165,0,0.1)'),
            'high': ('#991b1b', 'rgba(239,68,68,0.1)'),
        }
        text_color, bg_color = colors.get(obj.priority, ('#6c757d', '#f0f4f8'))
        label = {'low': '🟢 Low', 'medium': '🟡 Medium', 'high': '🔴 High'}.get(obj.priority, obj.priority)
        return format_html(
            '<span style="background:{};color:{};padding:3px 12px;border-radius:20px;font-weight:700;font-size:0.78rem;">{}</span>',
            bg_color, text_color, label
        )
    get_priority_badge.short_description = 'Priority'

    def get_active_status(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background:rgba(34,197,94,0.1);color:#166534;padding:3px 12px;border-radius:20px;font-weight:700;font-size:0.78rem;">✓ Active</span>'
            )
        return format_html(
            '<span style="background:rgba(239,68,68,0.1);color:#991b1b;padding:3px 12px;border-radius:20px;font-weight:700;font-size:0.78rem;">✗ Inactive</span>'
        )
    get_active_status.short_description = 'Status'

    @admin.action(description='Activate selected announcements')
    def activate_announcements(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} announcement(s) activated.')

    @admin.action(description='Deactivate selected announcements')
    def deactivate_announcements(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} announcement(s) deactivated.')