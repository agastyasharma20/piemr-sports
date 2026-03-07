import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseForbidden
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings

from .models import (Team, Achievement, Opportunity, StudentInterestForm,
                     EventRegistration, StudentProfile, Announcement)
from .forms import (UserRegistrationForm, OnboardingStep1Form, OnboardingStep2Form,
                    OnboardingStep3Form, OnboardingStep4Form,
                    StudentInterestFormForm, EventRegistrationForm)


# ========================
# ONBOARDING MIDDLEWARE HELPER
# ========================

def check_onboarding(user):
    """Returns redirect URL if onboarding incomplete, else None"""
    if not user.is_authenticated or user.is_staff:
        return None
    try:
        profile = user.student_profile
        if not profile.onboarding_complete:
            step = profile.onboarding_step
            urls = {0: 'onboarding_step1', 1: 'onboarding_step1',
                    2: 'onboarding_step2', 3: 'onboarding_step3'}
            return urls.get(step, 'onboarding_step1')
    except StudentProfile.DoesNotExist:
        return 'onboarding_step1'
    return None


# ========================
# PUBLIC VIEWS
# ========================

def home(request):
    redirect_url = check_onboarding(request.user)
    if redirect_url:
        return redirect(redirect_url)

    announcements = Announcement.objects.filter(is_active=True)[:5]
    context = {
        'featured_achievements': Achievement.objects.filter(is_featured=True)[:6],
        'upcoming_events': Opportunity.objects.filter(status='open').order_by('start_date')[:3],
        'total_teams': Team.objects.filter(is_active=True).count(),
        'total_achievements': Achievement.objects.count(),
        'announcements': announcements,
    }
    return render(request, 'sports_app/home.html', context)


def teams_list(request):
    redirect_url = check_onboarding(request.user)
    if redirect_url:
        return redirect(redirect_url)

    sport_filter = request.GET.get('sport', '')
    query = request.GET.get('q', '')
    teams = Team.objects.filter(is_active=True)
    if sport_filter:
        teams = teams.filter(sport=sport_filter)
    if query:
        teams = teams.filter(Q(name__icontains=query) | Q(description__icontains=query))
    return render(request, 'sports_app/teams_list.html', {
        'teams': teams, 'sports': Team.SPORT_CHOICES,
        'selected_sport': sport_filter, 'query': query,
    })


def team_detail(request, team_id):
    redirect_url = check_onboarding(request.user)
    if redirect_url:
        return redirect(redirect_url)

    team = get_object_or_404(Team, id=team_id)
    return render(request, 'sports_app/team_detail.html', {
        'team': team,
        'achievements': team.achievements.all()[:10],
        'opportunities': team.opportunities.filter(status='open'),
    })


def achievements_list(request):
    redirect_url = check_onboarding(request.user)
    if redirect_url:
        return redirect(redirect_url)

    achievements = Achievement.objects.all()
    query = request.GET.get('q', '')
    team_filter = request.GET.get('team', '')
    type_filter = request.GET.get('type', '')
    year_filter = request.GET.get('year', '')

    if query:
        achievements = achievements.filter(
            Q(title__icontains=query) | Q(player_names__icontains=query) |
            Q(description__icontains=query)
        )
    if team_filter:
        achievements = achievements.filter(team__id=team_filter)
    if type_filter:
        achievements = achievements.filter(achievement_type=type_filter)
    if year_filter:
        achievements = achievements.filter(date__year=year_filter)

    years = sorted(set(
        Achievement.objects.values_list('date__year', flat=True)
    ), reverse=True)

    return render(request, 'sports_app/achievements_list.html', {
        'achievements': achievements.order_by('-date'),
        'teams': Team.objects.filter(is_active=True),
        'achievement_types': Achievement._meta.get_field('achievement_type').choices,
        'years': years,
        'selected_team': team_filter,
        'selected_type': type_filter,
        'selected_year': year_filter,
        'query': query,
    })


def opportunities_list(request):
    redirect_url = check_onboarding(request.user)
    if redirect_url:
        return redirect(redirect_url)

    status_filter = request.GET.get('status', 'open')
    query = request.GET.get('q', '')
    opportunities = Opportunity.objects.filter(status=status_filter)
    if query:
        opportunities = opportunities.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    return render(request, 'sports_app/opportunities_list.html', {
        'opportunities': opportunities.order_by('-start_date'),
        'statuses': Opportunity._meta.get_field('status').choices,
        'selected_status': status_filter,
        'query': query,
    })


def opportunity_detail(request, opportunity_id):
    redirect_url = check_onboarding(request.user)
    if redirect_url:
        return redirect(redirect_url)

    opportunity = get_object_or_404(Opportunity, id=opportunity_id)
    is_registered = False
    if request.user.is_authenticated:
        is_registered = EventRegistration.objects.filter(
            user=request.user, opportunity=opportunity).exists()
    return render(request, 'sports_app/opportunity_detail.html', {
        'opportunity': opportunity, 'is_registered': is_registered,
    })


# ========================
# AUTHENTICATION
# ========================

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create empty profile
            token = str(uuid.uuid4())
            StudentProfile.objects.create(
                user=user,
                onboarding_step=0,
                onboarding_complete=False,
                email_token=token,
            )
            # Send verification email
            verify_url = request.build_absolute_uri(f'/verify-email/{token}/')
            try:
                send_mail(
                    subject='Verify your PIEMR Sports Portal Email',
                    message=f'Hi {user.first_name},\n\nClick the link to verify your email:\n{verify_url}\n\nPIEMR Sports Portal',
                    from_email='sports@piemr.edu.in',
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except:
                pass  # Don't block registration if email fails

            login(request, user)
            messages.success(request, f'Welcome {user.first_name}! Please complete your profile.')
            return redirect('onboarding_step1')
    else:
        form = UserRegistrationForm()
    return render(request, 'sports_app/register.html', {'form': form})


def verify_email(request, token):
    try:
        profile = StudentProfile.objects.get(email_token=token)
        profile.email_verified = True
        profile.email_token = None
        profile.save()
        messages.success(request, 'Email verified successfully!')
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Invalid or expired verification link.')
    return redirect('home')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            # Check onboarding
            redirect_url = check_onboarding(user)
            if redirect_url:
                return redirect(redirect_url)
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'sports_app/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


# ========================
# ONBOARDING VIEWS
# ========================

@login_required(login_url='login')
def onboarding_step1(request):
    """Basic Info"""
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = OnboardingStep1Form(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            p = form.save(commit=False)
            p.onboarding_step = max(p.onboarding_step, 1)
            p.save()
            messages.success(request, 'Basic info saved!')
            return redirect('onboarding_step2')
    else:
        form = OnboardingStep1Form(instance=profile)
    return render(request, 'sports_app/onboarding/step1.html', {
        'form': form, 'step': 1, 'total': 4,
        'step_title': 'Basic Information',
    })


@login_required(login_url='login')
def onboarding_step2(request):
    """Sports History"""
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    if profile.onboarding_step < 1:
        return redirect('onboarding_step1')
    if request.method == 'POST':
        form = OnboardingStep2Form(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            p = form.save(commit=False)
            p.onboarding_step = max(p.onboarding_step, 2)
            p.save()
            messages.success(request, 'Sports history saved!')
            return redirect('onboarding_step3')
    else:
        form = OnboardingStep2Form(instance=profile)
    return render(request, 'sports_app/onboarding/step2.html', {
        'form': form, 'step': 2, 'total': 4,
        'step_title': 'Sports History',
    })


@login_required(login_url='login')
def onboarding_step3(request):
    """Sports Interests"""
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    if profile.onboarding_step < 2:
        return redirect('onboarding_step2')
    if request.method == 'POST':
        form = OnboardingStep3Form(request.POST, instance=profile)
        if form.is_valid():
            p = form.save(commit=False)
            p.onboarding_step = max(p.onboarding_step, 3)
            p.save()
            form.save_m2m()
            messages.success(request, 'Sports interests saved!')
            return redirect('onboarding_step4')
    else:
        form = OnboardingStep3Form(instance=profile)
    return render(request, 'sports_app/onboarding/step3.html', {
        'form': form, 'step': 3, 'total': 4,
        'step_title': 'Sports Interests',
    })


@login_required(login_url='login')
def onboarding_step4(request):
    """Physical Details"""
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    if profile.onboarding_step < 3:
        return redirect('onboarding_step3')
    if request.method == 'POST':
        form = OnboardingStep4Form(request.POST, instance=profile)
        if form.is_valid():
            p = form.save(commit=False)
            p.onboarding_step = 4
            p.onboarding_complete = True
            p.save()
            messages.success(request, '🎉 Profile complete! Welcome to PIEMR Sports Portal!')
            return redirect('home')
    else:
        form = OnboardingStep4Form(instance=profile)
    return render(request, 'sports_app/onboarding/step4.html', {
        'form': form, 'step': 4, 'total': 4,
        'step_title': 'Physical Details',
    })


# ========================
# STUDENT DASHBOARD
# ========================

@login_required(login_url='login')
def dashboard(request):
    redirect_url = check_onboarding(request.user)
    if redirect_url:
        return redirect(redirect_url)

    profile = request.user.student_profile
    registrations = EventRegistration.objects.filter(
        user=request.user).select_related('opportunity')
    interest_form = StudentInterestForm.objects.filter(user=request.user).first()
    announcements = Announcement.objects.filter(is_active=True)[:3]

    return render(request, 'sports_app/dashboard.html', {
        'profile': profile,
        'registrations': registrations,
        'interest_form': interest_form,
        'announcements': announcements,
    })


@login_required(login_url='login')
def submit_interest_form(request):
    redirect_url = check_onboarding(request.user)
    if redirect_url:
        return redirect(redirect_url)

    existing = StudentInterestForm.objects.filter(user=request.user).first()
    if request.method == 'POST':
        form = StudentInterestFormForm(request.POST, instance=existing)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            form.save_m2m()
            messages.success(request, 'Interest form submitted!')
            return redirect('dashboard')
    else:
        form = StudentInterestFormForm(instance=existing)
    return render(request, 'sports_app/submit_interest_form.html', {
        'form': form, 'is_editing': existing is not None,
    })


@login_required(login_url='login')
@require_http_methods(["POST"])
def register_event(request, opportunity_id):
    redirect_url = check_onboarding(request.user)
    if redirect_url:
        return redirect(redirect_url)

    opportunity = get_object_or_404(Opportunity, id=opportunity_id)
    if EventRegistration.objects.filter(user=request.user, opportunity=opportunity).exists():
        messages.warning(request, 'Already registered!')
        return redirect('opportunity_detail', opportunity_id=opportunity_id)
    form = EventRegistrationForm(request.POST)
    if form.is_valid():
        reg = form.save(commit=False)
        reg.user = request.user
        reg.opportunity = opportunity
        reg.save()
        messages.success(request, 'Registered successfully!')
    return redirect('opportunity_detail', opportunity_id=opportunity_id)


@login_required(login_url='login')
def cancel_registration(request, registration_id):
    registration = get_object_or_404(EventRegistration, id=registration_id)
    if registration.user != request.user:
        return HttpResponseForbidden()
    registration.status = 'cancelled'
    registration.save()
    messages.success(request, 'Registration cancelled.')
    return redirect('dashboard')


@login_required(login_url='login')
@login_required(login_url='login')
def admin_dashboard(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()
    return render(request, 'sports_app/admin_dashboard.html', {
        'total_interest_forms': StudentInterestForm.objects.count(),
        'total_registrations': EventRegistration.objects.count(),
        'pending_registrations': EventRegistration.objects.filter(status='registered').count(),
        'total_teams': Team.objects.filter(is_active=True).count(),
        'recent_interest_forms': StudentInterestForm.objects.order_by('-submission_date')[:8],
        'recent_registrations': EventRegistration.objects.order_by('-registration_date')[:8],
        'announcements': Announcement.objects.filter(is_active=True)[:5],
    })
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from django.http import HttpResponse
from datetime import datetime
def announcements_list(request):
    announcements = Announcement.objects.filter(is_active=True)
    return render(request, 'sports_app/announcements.html', {
        'announcements': announcements
    })

@login_required(login_url='login')
def export_interest_forms_excel(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Student Interest Forms"

    # --- Styling ---
    header_font = Font(bold=True, color="FFFFFF", size=12)
    header_fill = PatternFill("solid", fgColor="1a3c6e")
    center = Alignment(horizontal="center", vertical="center")
    border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )

    # --- Title Row ---
    ws.merge_cells('A1:K1')
    title_cell = ws['A1']
    title_cell.value = "PIEMR Sports Portal — Student Interest Forms"
    title_cell.font = Font(bold=True, size=14, color="1a3c6e")
    title_cell.alignment = center
    ws.row_dimensions[1].height = 30

    # --- Generated date row ---
    ws.merge_cells('A2:K2')
    ws['A2'] = f"Generated on: {datetime.now().strftime('%d %B %Y, %I:%M %p')}"
    ws['A2'].font = Font(italic=True, color="666666")
    ws['A2'].alignment = center

    # --- Empty row ---
    ws.append([])

    # --- Headers ---
    headers = [
        'S.No', 'Name', 'Roll Number', 'Email', 'Phone',
        'Branch', 'Year', 'Experience Level',
        'Sports Interests', 'Past Achievements', 'Submission Date'
    ]
    ws.append(headers)
    header_row = ws.row_dimensions[4]
    header_row.height = 20

    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col_num)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center
        cell.border = border

    # --- Data Rows ---
    forms = StudentInterestForm.objects.all().order_by('-submission_date')
    alt_fill = PatternFill("solid", fgColor="EBF1F8")

    for idx, form in enumerate(forms, 1):
        sports = ", ".join([t.name for t in form.sports_interests.all()])
        row_data = [
            idx,
            form.name,
            form.roll_number,
            form.email,
            form.phone,
            form.branch,
            f"Year {form.year}",
            form.get_experience_level_display(),
            sports,
            form.past_achievements or "—",
            form.submission_date.strftime('%d/%m/%Y'),
        ]
        ws.append(row_data)

        # Alternate row colors
        fill = alt_fill if idx % 2 == 0 else PatternFill("solid", fgColor="FFFFFF")
        for col_num in range(1, len(headers) + 1):
            cell = ws.cell(row=idx + 4, column=col_num)
            cell.fill = fill
            cell.border = border
            cell.alignment = Alignment(vertical="center", wrap_text=True)

    # --- Column Widths ---
    column_widths = [6, 20, 15, 28, 14, 18, 8, 18, 30, 40, 14]
    for i, width in enumerate(column_widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = width

    # --- Summary Sheet ---
    ws2 = wb.create_sheet(title="Summary")
    ws2['A1'] = "PIEMR Sports Portal — Summary"
    ws2['A1'].font = Font(bold=True, size=14, color="1a3c6e")
    ws2.merge_cells('A1:C1')

    ws2.append([])
    summary_headers = ['Metric', 'Count', 'Details']
    ws2.append(summary_headers)
    for col in range(1, 4):
        cell = ws2.cell(row=3, column=col)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center
        cell.border = border

    # Summary data
    from collections import Counter
    all_forms = StudentInterestForm.objects.all()
    branch_counts = Counter(all_forms.values_list('branch', flat=True))
    exp_counts = Counter(all_forms.values_list('experience_level', flat=True))

    summary_data = [
        ['Total Interest Forms', StudentInterestForm.objects.count(), ''],
        ['Total Event Registrations', EventRegistration.objects.count(), ''],
        ['Total Teams', Team.objects.filter(is_active=True).count(), ''],
        ['Total Achievements', Achievement.objects.count(), ''],
        ['', '', ''],
        ['Experience Breakdown', '', ''],
        ['— Beginners', exp_counts.get('beginner', 0), ''],
        ['— Intermediate', exp_counts.get('intermediate', 0), ''],
        ['— Advanced', exp_counts.get('advanced', 0), ''],
        ['— Professional', exp_counts.get('professional', 0), ''],
    ]

    for row in summary_data:
        ws2.append(row)

    for col in ['A', 'B', 'C']:
        ws2.column_dimensions[col].width = 30

    # --- Return as download ---
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"PIEMR_Sports_Interest_Forms_{datetime.now().strftime('%d%m%Y')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response


@login_required(login_url='login')
def export_registrations_excel(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Event Registrations"

    header_font = Font(bold=True, color="FFFFFF", size=12)
    header_fill = PatternFill("solid", fgColor="1a3c6e")
    center = Alignment(horizontal="center", vertical="center")
    border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )

    ws.merge_cells('A1:H1')
    ws['A1'] = "PIEMR Sports Portal — Event Registrations"
    ws['A1'].font = Font(bold=True, size=14, color="1a3c6e")
    ws['A1'].alignment = center
    ws.row_dimensions[1].height = 30

    ws.merge_cells('A2:H2')
    ws['A2'] = f"Generated on: {datetime.now().strftime('%d %B %Y, %I:%M %p')}"
    ws['A2'].font = Font(italic=True, color="666666")
    ws['A2'].alignment = center

    ws.append([])

    headers = ['S.No', 'Student Name', 'Event', 'Team Name',
               'Contact', 'Registration Date', 'Status', 'Notes']
    ws.append(headers)

    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col_num)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center
        cell.border = border

    registrations = EventRegistration.objects.all().select_related(
        'user', 'opportunity').order_by('-registration_date')
    alt_fill = PatternFill("solid", fgColor="EBF1F8")

    for idx, reg in enumerate(registrations, 1):
        row_data = [
            idx,
            reg.user.get_full_name() or reg.user.username,
            reg.opportunity.title,
            reg.team_name or "Individual",
            reg.contact_number,
            reg.registration_date.strftime('%d/%m/%Y'),
            reg.get_status_display(),
            reg.notes or "—",
        ]
        ws.append(row_data)

        fill = alt_fill if idx % 2 == 0 else PatternFill("solid", fgColor="FFFFFF")
        for col_num in range(1, len(headers) + 1):
            cell = ws.cell(row=idx + 4, column=col_num)
            cell.fill = fill
            cell.border = border
            cell.alignment = Alignment(vertical="center")

    col_widths = [6, 22, 35, 20, 14, 16, 14, 30]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"PIEMR_Event_Registrations_{datetime.now().strftime('%d%m%Y')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response


@login_required(login_url='login')
def export_student_profiles_excel(request):
    """Export all student profiles — physical details + sports interests"""
    if not request.user.is_staff:
        return HttpResponseForbidden()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Student Profiles"

    header_font = Font(bold=True, color="FFFFFF", size=12)
    header_fill = PatternFill("solid", fgColor="1a3c6e")
    center = Alignment(horizontal="center", vertical="center")
    border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )

    ws.merge_cells('A1:N1')
    ws['A1'] = "PIEMR Sports Portal — Complete Student Profiles"
    ws['A1'].font = Font(bold=True, size=14, color="1a3c6e")
    ws['A1'].alignment = center
    ws.row_dimensions[1].height = 30

    ws.merge_cells('A2:N2')
    ws['A2'] = f"Generated on: {datetime.now().strftime('%d %B %Y, %I:%M %p')}"
    ws['A2'].font = Font(italic=True, color="666666")
    ws['A2'].alignment = center
    ws.append([])

    headers = [
        'S.No', 'Full Name', 'Email', 'Roll No', 'Branch', 'Year',
        'Phone', 'Experience', 'Sports Interests', 'Position',
        'Height (cm)', 'Weight (kg)', 'Fitness Level', 'Joined On'
    ]
    ws.append(headers)

    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col_num)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center
        cell.border = border

    profiles = StudentProfile.objects.filter(
        onboarding_complete=True
    ).select_related('user').prefetch_related('sports_interests')

    alt_fill = PatternFill("solid", fgColor="EBF1F8")

    for idx, profile in enumerate(profiles, 1):
        sports = ", ".join([t.name for t in profile.sports_interests.all()])
        row_data = [
            idx,
            profile.user.get_full_name() or profile.user.username,
            profile.user.email,
            profile.roll_number or "—",
            profile.branch or "—",
            f"Year {profile.year}" if profile.year else "—",
            profile.phone or "—",
            profile.get_experience_level_display() if profile.experience_level else "—",
            sports or "—",
            profile.position_played or "—",
            profile.height_cm or "—",
            profile.weight_kg or "—",
            profile.get_fitness_level_display() if profile.fitness_level else "—",
            profile.created_at.strftime('%d/%m/%Y'),
        ]
        ws.append(row_data)

        fill = alt_fill if idx % 2 == 0 else PatternFill("solid", fgColor="FFFFFF")
        for col_num in range(1, len(headers) + 1):
            cell = ws.cell(row=idx + 4, column=col_num)
            cell.fill = fill
            cell.border = border
            cell.alignment = Alignment(vertical="center", wrap_text=True)

    col_widths = [6, 22, 28, 15, 18, 8, 14, 16, 30, 18, 12, 12, 16, 14]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"PIEMR_Student_Profiles_{datetime.now().strftime('%d%m%Y')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response

def search_results(request):
    query = request.GET.get('q', '').strip()
    teams, achievements, opportunities = [], [], []

    if query:
        teams = Team.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query) |
            Q(sport__icontains=query) | Q(coach_name__icontains=query)
        ).filter(is_active=True)

        achievements = Achievement.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query) |
            Q(player_names__icontains=query) | Q(location__icontains=query)
        )

        opportunities = Opportunity.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query) |
            Q(event_type__icontains=query) | Q(location__icontains=query)
        )

    total = len(teams) + len(achievements) + len(opportunities)

    return render(request, 'sports_app/search_results.html', {
        'query': query,
        'teams': teams,
        'achievements': achievements,
        'opportunities': opportunities,
        'total': total,
    })

@login_required(login_url='login')
def student_profile(request, user_id):
    from django.contrib.auth.models import User as AuthUser
    profile_user = get_object_or_404(AuthUser, id=user_id)

    # Only allow viewing own profile unless staff
    if profile_user != request.user and not request.user.is_staff:
        messages.error(request, 'You can only view your own profile.')
        return redirect('dashboard')

    try:
        profile = profile_user.student_profile
    except StudentProfile.DoesNotExist:
        profile = None

    registrations = EventRegistration.objects.filter(
        user=profile_user, status__in=['registered','confirmed','participated']
    ).select_related('opportunity')[:5]

    return render(request, 'sports_app/student_profile.html', {
        'profile_user': profile_user,
        'profile': profile,
        'registrations': registrations,
    })