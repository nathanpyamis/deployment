from django.contrib import admin
from .models import ApplicantProfile, Application

@admin.register(ApplicantProfile)
class ApplicantProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'institution', 'course', 'status', 'submission_date')
    list_filter = ('status', 'institution', 'submission_date')
    search_fields = ('applicant__user__username', 'applicant__user__first_name', 'institution__name')