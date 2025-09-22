from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import ApplicantProfile, Application
from applications.forms import SignupForm, ApplicationForm, UserRegistrationForm, UserLoginForm
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.db.models import Q, Count
from django.contrib.admin.views.decorators import staff_member_required
from utils.ai_scanner import scan_documents_for_eligibility
from institutions.models import Institution
from django.db.models import Sum
from finance.models import Payment  # assuming this exists
from applications.models import Application
from django.dispatch import receiver
from allauth.account.signals import user_logged_in
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.auth.forms import SetPasswordForm
from utils.decorators import require_password_setup

def redirect_user_dashboard(user):
    if user.groups.filter(name='Scholarship Officers').exists():
        return redirect('applications:officer_dashboard')

    profile = ApplicantProfile.objects.filter(user=user).first()
    if profile and Application.objects.filter(applicant=profile).exists():
        return redirect('applications:user_dashboard')  # ✅ student dashboard
    else:
        return redirect('applications:create_application')  # ✅ new applicant

# --- Home ---


def home_view(request):
    total_applicants = Application.objects.count()
    total_awarded = Application.objects.filter(status='awarded').count()

    institution_stats = (
        Application.objects
        .values('institution__name')
        .annotate(
            applicants=Count('id'),
            awarded=Count('id', filter=Q(status='awarded'))
        )
        .order_by('-applicants')
    )

    context = {
        'total_applicants': total_applicants,
        'total_awarded': total_awarded,
        'institution_stats': institution_stats,
    }
    return render(request, 'home.html', context)

# --- Officer check ---

def is_scholarship_officer(user):
    return user.is_authenticated and user.groups.filter(name='Scholarship Officers').exists()

@user_passes_test(is_scholarship_officer)
def officer_view_student_profile(request, pk):
    student = get_object_or_404(ApplicantProfile, pk=pk)
    return render(request, 'applications/officer_student_profile.html', {'student': student})

# --- Authentication ---
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully. Please log in.")
            return redirect('applications:login')
        else:
            messages.error(request, "Signup failed. Please correct the errors below.")
    else:
        form = SignupForm()
    return render(request, 'applications/signup.html', {'crispy_form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('create_application')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Registration successful! Welcome, {user.username}.')
            return redirect('create_application')
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    return render(request, 'applications/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect_user_dashboard(request.user)

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect_user_dashboard(user)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()

    return render(request, 'applications/login.html', {'form': form})


def logout_view(request):
    is_officer = request.user.groups.filter(name='Scholarship Officers').exists()
    logout(request)
    if is_officer:
        messages.info(request, "Officer session ended. Please log in again.")
    else:
        messages.success(request, "You have been logged out successfully.")
    return redirect('applications:login')



class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class UserLoginForm(AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


# --- Applicant ---

@login_required
def create_application(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            profile, _ = ApplicantProfile.objects.get_or_create(user=request.user)

            # Save profile photo if uploaded
            if 'photo' in request.FILES:
                profile.photo = request.FILES['photo']
                profile.save()

            # Save application
            application = form.save(commit=False)
            application.applicant = profile
            application.save()

            # 🔍 Run AI scanner after saving
            scan_result = scan_documents_for_eligibility(application)

            # Optionally store the result in a field or log it
            application.reviewer_note = scan_result  # or save to a separate model/log
            application.save()

            messages.success(request, "Application submitted and scanned for eligibility.")
            return redirect('applications:application_success')
    else:
        form = ApplicationForm()

    return render(request, 'applications/application_form.html', {'form': form})


@login_required
def application_success(request):
    return redirect('applications:user_dashboard')

# --- Officer ---
def is_scholarship_officer(user):
    return user.is_authenticated and user.groups.filter(name='Scholarship Officers').exists()

@user_passes_test(is_scholarship_officer)
def officer_dashboard(request):
    query = request.GET.get('q', '')
    applications = Application.objects.select_related('applicant__user', 'institution', 'course')

    if query:
        applications = applications.filter(
            Q(applicant__user__first_name__icontains=query) |
            Q(applicant__user__last_name__icontains=query) |
            Q(institution__name__icontains=query)
        )

    applications = applications.order_by('-submission_date')

    # ✅ Build institution-level stats
    institution_stats = {}
    for institution in Institution.objects.all():
        stats = {
            'total': institution.applications.count(),
            'approved': institution.applications.filter(status='APPROVED').count(),
            'rejected': institution.applications.filter(status='REJECTED').count(),
            'pending': institution.applications.filter(status='PENDING').count(),
        }
        institution_stats[institution.id] = stats

    return render(request, 'applications/officer_dashboard.html', {
        'applications': applications,
        'institution_stats': institution_stats
    })

@user_passes_test(is_scholarship_officer)
def officer_view_profile(request, pk):
    application = get_object_or_404(Application.objects.select_related('applicant__user', 'institution', 'course'), pk=pk)
    
    documents = [
        ('Grade 12 Certificate', application.grade_12_certificate),
        ('Academic Transcript', application.transcript),
        ('Acceptance Letter', application.acceptance_letter),
        ('School Fee Structure', application.school_fee_structure),
        ('Student ID Card', application.id_card),
        ('Character Reference 1', application.character_reference_1),
        ('Character Reference 2', application.character_reference_2),
        ('Expression Of Interest', application.expression_of_interest),
    ]

    return render(request, 'applications/officer_view_profile.html', {
        'application': application,
        'documents': documents
    })

# --AI Scan ---
@staff_member_required
def review_application(request, pk):
    application = get_object_or_404(Application, pk=pk)

    if request.method == 'POST':
        status = request.POST.get('status')
        note = request.POST.get('reviewer_note')
        application.status = status
        application.reviewer_note = note
        application.save()
        messages.success(request, "Application updated successfully.")
        return redirect('applications:officer_dashboard')

    return render(request, 'applications/review_application.html', {'application': application})

@require_password_setup
@login_required
def user_dashboard(request):
    profile = get_object_or_404(ApplicantProfile, user=request.user)
    applications = Application.objects.filter(applicant=profile).select_related('institution', 'course')

    enriched_apps = []
    for app in applications:
        # 📁 Document summary
        documents = [
            ('Grade 12 Certificate', app.grade_12_certificate),
            ('Academic Transcript', app.transcript),
            ('Acceptance Letter', app.acceptance_letter),
            ('School Fee Structure', app.school_fee_structure),
            ('Student ID Card', app.id_card),
            ('Character Reference 1', app.character_reference_1),
            ('Character Reference 2', app.character_reference_2),
            ('Expression Of Interest', app.expression_of_interest),
        ]

        # 💰 Payment summary
        total_paid = Payment.objects.filter(application=app).aggregate(total=Sum('amount'))['total'] or 0
        total_fee = app.course.total_tuition_fee
        balance = total_fee - total_paid
        payment_status = (
            'Fully Paid' if total_paid >= total_fee else
            'Partially Paid' if total_paid > 0 else
            'Unpaid'
        )

        enriched_apps.append({
            'app': app,
            'documents': documents,
            'total_paid': total_paid,
            'balance': balance,
            'payment_status': payment_status
        })

    return render(request, 'applications/applicant_dashboard.html', {
        'applications': enriched_apps,
        'profile': profile,
    })

#Email password creation

#@receiver(user_logged_in)
#def send_password_setup_email(sender, request, user, **kwargs):
#    if not user.has_usable_password():
#        setup_url = request.build_absolute_uri(reverse('applications:set_password'))
#        send_mail(
#            subject='Set Your Password for GSSS Portal',
#            message=f'Hi {user.first_name},\n\nYou signed in with Google. To enable password login, please set your password here:\n{setup_url}',
#            from_email='noreply@gsss.com',
#            recipient_list=[user.email],
#            fail_silently=False,
#        )

#@login_required
#def set_password_view(request):
#    form = SetPasswordForm(request.user, request.POST or None)
#    if request.method == 'POST' and form.is_valid():
#        form.save()
#        return redirect('applications:dashboard')  # or wherever you want to go
#    return render(request, 'applications/set_password.html', {'form': form})

