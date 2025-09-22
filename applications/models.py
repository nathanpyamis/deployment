from django.db import models
from django.contrib.auth.models import User
from institutions.models import Institution, Course

class ApplicantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Application(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    applicant = models.ForeignKey(ApplicantProfile, on_delete=models.CASCADE, related_name='applications')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='applications', default=1)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    year_of_study = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    reviewer_note = models.TextField(blank=True)
    ai_summary = models.TextField(blank=True, null=True)
    # Document Uploads
    grade_12_certificate = models.FileField(upload_to='documents/certificates/')
    transcript = models.FileField(upload_to='documents/transcripts/')
    acceptance_letter = models.FileField(upload_to='documents/acceptance_letters/')
    school_fee_structure = models.FileField(upload_to='documents/fee_structures/')
    id_card = models.FileField(upload_to='documents/ids/')
    character_reference_1 = models.FileField(upload_to='documents/references/')
    character_reference_2 = models.FileField(upload_to='documents/references/')
    expression_of_interest = models.FileField(upload_to='documents/expression_letters/', blank=True, null=True)


    # 👨‍👩‍👧 Parents Financial Info
    parent_employed = models.BooleanField(default=False)
    parent_company = models.CharField(max_length=255, blank=True)
    parent_job_title = models.CharField(max_length=255, blank=True)
    parent_salary_range = models.CharField(max_length=100, blank=True)
    parent_income_source = models.CharField(max_length=255, blank=True)
    parent_annual_income = models.CharField(max_length=100, blank=True)

    # 👨‍🎓 Student Financial Info
    student_employed = models.BooleanField(default=False)
    student_company = models.CharField(max_length=255, blank=True)
    student_job_title = models.CharField(max_length=255, blank=True)
    student_salary_range = models.CharField(max_length=100, blank=True)

    # 🌍 Additional Student Info
    origin_province = models.CharField(max_length=100, blank=True)
    origin_district = models.CharField(max_length=100, blank=True)
    origin_ward = models.CharField(max_length=100, blank=True)

    residency_province = models.CharField(max_length=100, blank=True)
    residency_district = models.CharField(max_length=100, blank=True)
    residency_ward = models.CharField(max_length=100, blank=True)
    residency_years = models.PositiveIntegerField(default=0)

    submission_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Application for {self.applicant.user.username} - {self.status}"

    class Meta:
        ordering = ['-submission_date']
