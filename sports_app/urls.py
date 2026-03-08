from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [

    # ─── PUBLIC ───────────────────────────────────────────────
    path('', views.home, name='home'),
    path('teams/', views.teams_list, name='teams_list'),
    path('teams/<int:team_id>/', views.team_detail, name='team_detail'),
    path('achievements/', views.achievements_list, name='achievements_list'),
    path('opportunities/', views.opportunities_list, name='opportunities_list'),
    path('opportunities/<int:opportunity_id>/', views.opportunity_detail, name='opportunity_detail'),
    path('announcements/', views.announcements_list, name='announcements_list'),
    path('search/', views.search_results, name='search_results'),
    path('gallery/', views.gallery, name='gallery'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),

    # ─── AUTH ─────────────────────────────────────────────────
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),

    # ─── PASSWORD RESET ───────────────────────────────────────
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='sports_app/password_reset.html'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='sports_app/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='sports_app/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='sports_app/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    # ─── ONBOARDING ───────────────────────────────────────────
    path('onboarding/step1/', views.onboarding_step1, name='onboarding_step1'),
    path('onboarding/step2/', views.onboarding_step2, name='onboarding_step2'),
    path('onboarding/step3/', views.onboarding_step3, name='onboarding_step3'),
    path('onboarding/step4/', views.onboarding_step4, name='onboarding_step4'),

    # ─── STUDENT ──────────────────────────────────────────────
    path('dashboard/', views.dashboard, name='dashboard'),
    path('complete-profile/', views.onboarding_step1, name='complete_profile'),
    path('profile/<int:user_id>/', views.student_profile, name='student_profile'),
    path('submit-interest-form/', views.submit_interest_form, name='submit_interest_form'),
    path('register-event/<int:opportunity_id>/', views.register_event, name='register_event'),
    path('cancel-registration/<int:registration_id>/', views.cancel_registration, name='cancel_registration'),

    # ─── ADMIN ────────────────────────────────────────────────
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/award-badge/', views.award_badge, name='award_badge'),
    path('admin/issue-certificate/', views.issue_certificate, name='issue_certificate'),

    # ─── EXPORTS ──────────────────────────────────────────────
    path('export/interest-forms/', views.export_interest_forms_excel, name='export_interest_forms'),
    path('export/registrations/', views.export_registrations_excel, name='export_registrations'),
    path('export/student-profiles/', views.export_student_profiles_excel, name='export_student_profiles'),
]