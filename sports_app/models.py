import os
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Announcement(models.Model):
    """Notifications and announcements from sports department"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High — Show as Banner'),
    ]
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class StudentProfile(models.Model):
    """Extended user profile for students — filled during onboarding"""

    YEAR_CHOICES = [(1,'1st Year'),(2,'2nd Year'),(3,'3rd Year'),(4,'4th Year')]
    EXPERIENCE_CHOICES = [
        ('beginner','Beginner'),
        ('intermediate','Intermediate'),
        ('advanced','Advanced'),
        ('professional','Professional'),
    ]
    FITNESS_CHOICES = [
        ('low','Low — Just getting started'),
        ('moderate','Moderate — Regular exercise'),
        ('high','High — Athlete level'),
        ('elite','Elite — Competitive level'),
    ]
    ONBOARDING_STEPS = [
        (0,'Not Started'),
        (1,'Basic Info Done'),
        (2,'Sports History Done'),
        (3,'Sports Interests Done'),
        (4,'Complete'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')

    # --- STEP 1: Basic Info ---
    roll_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    branch = models.CharField(max_length=50, null=True, blank=True)
    year = models.IntegerField(choices=YEAR_CHOICES, null=True, blank=True)
    phone = models.CharField(max_length=10, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='student_profiles/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('male','Male'),('female','Female'),('other','Other')], null=True, blank=True)

    # --- STEP 2: Sports History ---
    past_achievements = models.TextField(null=True, blank=True, help_text="Describe your past sports achievements")
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, null=True, blank=True)
    years_playing = models.IntegerField(null=True, blank=True, help_text="How many years have you been playing sports?")
    highest_level = models.CharField(max_length=100, null=True, blank=True, help_text="e.g. District level, State level, National level")
    certificates = models.FileField(upload_to='certificates/', null=True, blank=True)

    # --- STEP 3: Sports Interests ---
    sports_interests = models.ManyToManyField('Team', blank=True, related_name='interested_students')
    position_played = models.CharField(max_length=100, null=True, blank=True, help_text="e.g. Batsman, Goalkeeper, Striker")
    availability = models.CharField(max_length=20, choices=[
        ('morning','Morning'),('evening','Evening'),('both','Both'),('weekends','Weekends Only')
    ], null=True, blank=True)
    willing_to_travel = models.BooleanField(default=False)

    # --- STEP 4: Physical Details ---
    height_cm = models.IntegerField(null=True, blank=True, help_text="Height in cm")
    weight_kg = models.IntegerField(null=True, blank=True, help_text="Weight in kg")
    fitness_level = models.CharField(max_length=10, choices=FITNESS_CHOICES, null=True, blank=True)
    medical_conditions = models.TextField(null=True, blank=True, help_text="Any medical conditions the coach should know about")

    # --- ONBOARDING TRACKING ---
    onboarding_step = models.IntegerField(choices=ONBOARDING_STEPS, default=0)
    onboarding_complete = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    email_token = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} - {self.roll_number}"

    @property
    def completion_percentage(self):
        return (self.onboarding_step / 4) * 100

    class Meta:
        verbose_name_plural = "Student Profiles"


class Team(models.Model):
    SPORT_CHOICES = [
        ('cricket','Cricket'),('football','Football'),
        ('basketball','Basketball'),('volleyball','Volleyball'),
        ('badminton','Badminton'),('table_tennis','Table Tennis'),
        ('athletics','Athletics'),('swimming','Swimming'),('other','Other'),
    ]
    name = models.CharField(max_length=100)
    sport = models.CharField(max_length=50, choices=SPORT_CHOICES)
    description = models.TextField()
    coach_name = models.CharField(max_length=100)
    coach_email = models.EmailField()
    coach_phone = models.CharField(max_length=10)
    team_logo = models.ImageField(upload_to='team_logos/', null=True, blank=True)
    members_count = models.IntegerField(default=0)
    establishment_year = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.sport})"

    class Meta:
        ordering = ['sport','name']


class Achievement(models.Model):
    ACHIEVEMENT_TYPES = [
        ('championship','Championship'),('medal','Medal'),
        ('award','Award'),('record','Record'),('recognition','Recognition'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='achievements')
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    date = models.DateField()
    location = models.CharField(max_length=100)
    player_names = models.TextField(help_text="Player names separated by commas")
    image = models.ImageField(upload_to='achievements/', null=True, blank=True)
    certificate_image = models.ImageField(upload_to='certificates/', null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.team.name}"

    class Meta:
        ordering = ['-date']


class Opportunity(models.Model):
    STATUS_CHOICES = [
        ('open','Open for Registration'),('closed','Closed'),
        ('completed','Completed'),('postponed','Postponed'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='opportunities')
    event_type = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    registration_deadline = models.DateTimeField()
    max_participants = models.IntegerField(null=True, blank=True)
    eligibility_criteria = models.TextField()
    poster_image = models.ImageField(upload_to='opportunity_posters/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    contact_person = models.CharField(max_length=100)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.team.name}"

    class Meta:
        ordering = ['-start_date']


class StudentInterestForm(models.Model):
    EXPERIENCE_LEVEL = [
        ('beginner','Beginner'),('intermediate','Intermediate'),
        ('advanced','Advanced'),('professional','Professional'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interest_forms')
    roll_number = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    branch = models.CharField(max_length=50)
    year = models.IntegerField()
    past_achievements = models.TextField(blank=True)
    sports_interests = models.ManyToManyField(Team)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL)
    additional_comments = models.TextField(blank=True)
    submission_date = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.roll_number}"

    class Meta:
        ordering = ['-submission_date']


class EventRegistration(models.Model):
    STATUS_CHOICES = [
        ('registered','Registered'),('confirmed','Confirmed'),
        ('participated','Participated'),('cancelled','Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='registrations')
    team_name = models.CharField(max_length=100, blank=True)
    team_members = models.TextField(blank=True)
    contact_number = models.CharField(max_length=10)
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered')
    confirmation_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.first_name} - {self.opportunity.title}"

    class Meta:
        ordering = ['-registration_date']
        unique_together = ['user','opportunity']