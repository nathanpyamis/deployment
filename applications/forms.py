from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Application

# --- Application Form ---
class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            'institution', 'course', 'year_of_study',
            'grade_12_certificate', 'transcript', 'acceptance_letter',
            'school_fee_structure', 'id_card',
            'character_reference_1', 'character_reference_2',
            'expression_of_interest',

            # Parents Financial Info
            'parent_employed', 'parent_company', 'parent_job_title',
            'parent_salary_range', 'parent_income_source', 'parent_annual_income',

            # Student Financial Info
            'student_employed', 'student_company', 'student_job_title',
            'student_salary_range',

            # Additional Student Info
            'origin_province', 'origin_district', 'origin_ward',
            'residency_province', 'residency_district', 'residency_ward',
            'residency_years',
        ]
        widgets = {
            'institution': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'year_of_study': forms.NumberInput(attrs={'class': 'form-control'}),

            # Parent Financial Info
            'parent_company': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_salary_range': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_income_source': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_annual_income': forms.TextInput(attrs={'class': 'form-control'}),

            # Student Financial Info
            'student_company': forms.TextInput(attrs={'class': 'form-control'}),
            'student_job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'student_salary_range': forms.TextInput(attrs={'class': 'form-control'}),

            # Additional Info
            'origin_province': forms.TextInput(attrs={'class': 'form-control'}),
            'origin_district': forms.TextInput(attrs={'class': 'form-control'}),
            'origin_ward': forms.TextInput(attrs={'class': 'form-control'}),
            'residency_province': forms.TextInput(attrs={'class': 'form-control'}),
            'residency_district': forms.TextInput(attrs={'class': 'form-control'}),
            'residency_ward': forms.TextInput(attrs={'class': 'form-control'}),
            'residency_years': forms.NumberInput(attrs={'class': 'form-control'}),
        }


# --- Signup Form (used in /signup/) ---
class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")
    first_name = forms.CharField(max_length=30, required=True, help_text="Your given name.")
    last_name = forms.CharField(max_length=30, required=True, help_text="Your surname.")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

# --- User Registration Form (used in /register/) ---
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

# --- User Login Form (used in /login/) ---
class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'})
    )
