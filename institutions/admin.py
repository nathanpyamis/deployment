from django.contrib import admin
from .models import Institution, Course

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'phone', 'email')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('location',)
    fields = ('name', 'location', 'phone', 'email')  # Optional: controls form layout


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'institution', 'years_of_study', 'total_tuition_fee')
    list_filter = ('institution',)
    search_fields = ('name', 'institution__name')