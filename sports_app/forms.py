from django import forms
from django.contrib.auth.models import User
from .models import StudentProfile, StudentInterestForm, EventRegistration, Team


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Create a strong password'
    }))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Confirm your password'
    }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your college email'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('password_confirm'):
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


# ---- ONBOARDING STEP FORMS ----

class OnboardingStep1Form(forms.ModelForm):
    """Basic Info"""
    class Meta:
        model = StudentProfile
        fields = ['roll_number', 'branch', 'year', 'phone',
                  'date_of_birth', 'gender', 'profile_picture']
        widgets = {
            'roll_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 51110105688'}),
            'branch': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Computer Science'}),
            'year': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit mobile number'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }


class OnboardingStep2Form(forms.ModelForm):
    """Sports History"""
    class Meta:
        model = StudentProfile
        fields = ['past_achievements', 'experience_level',
                  'years_playing', 'highest_level', 'certificates']
        widgets = {
            'past_achievements': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4,
                'placeholder': 'e.g. Won district cricket tournament 2023, School football captain...'
            }),
            'experience_level': forms.Select(attrs={'class': 'form-select'}),
            'years_playing': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 5'}),
            'highest_level': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. State level, District level'}),
            'certificates': forms.FileInput(attrs={'class': 'form-control'}),
        }


class OnboardingStep3Form(forms.ModelForm):
    """Sports Interests"""
    class Meta:
        model = StudentProfile
        fields = ['sports_interests', 'position_played', 'availability', 'willing_to_travel']
        widgets = {
            'sports_interests': forms.CheckboxSelectMultiple(),
            'position_played': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Batsman, Striker, Point Guard'}),
            'availability': forms.Select(attrs={'class': 'form-select'}),
            'willing_to_travel': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class OnboardingStep4Form(forms.ModelForm):
    """Physical Details"""
    class Meta:
        model = StudentProfile
        fields = ['height_cm', 'weight_kg', 'fitness_level', 'medical_conditions']
        widgets = {
            'height_cm': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Height in cm (e.g. 175)'}),
            'weight_kg': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Weight in kg (e.g. 70)'}),
            'fitness_level': forms.Select(attrs={'class': 'form-select'}),
            'medical_conditions': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Any medical conditions coaches should know about (leave blank if none)'
            }),
        }


class StudentInterestFormForm(forms.ModelForm):
    class Meta:
        model = StudentInterestForm
        fields = ['roll_number', 'name', 'email', 'phone', 'branch', 'year',
                  'past_achievements', 'sports_interests', 'experience_level', 'additional_comments']
        widgets = {
            'roll_number': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'branch': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.Select(attrs={'class': 'form-select'}),
            'past_achievements': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'sports_interests': forms.CheckboxSelectMultiple(),
            'experience_level': forms.Select(attrs={'class': 'form-select'}),
            'additional_comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class EventRegistrationForm(forms.ModelForm):
    class Meta:
        model = EventRegistration
        fields = ['team_name', 'team_members', 'contact_number']
        widgets = {
            'team_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Team name (if applicable)'}),
            'team_members': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Names separated by commas'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit number'}),
        }