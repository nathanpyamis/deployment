from django import forms
from .models import Course, Institution

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['institution', 'name', 'total_tuition_fee']
        widgets = {
            'institution': forms.HiddenInput(),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Course name'}),
            'total_tuition_fee': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total fee'}),
        }

