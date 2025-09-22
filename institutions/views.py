from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Institution, Course
from .forms import CourseForm
from applications.models import Application
from django.db.models import Count, Q

institution_stats = (
    Application.objects
    .values('institution__name')
    .annotate(
        applicants=Count('id'),
        awarded=Count('id', filter=Q(status='awarded'))
    )
    .order_by('-applicants')
)


def manage_institutions(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('institutions:manage')
    else:
        form = CourseForm()

    institutions = Institution.objects.prefetch_related('courses').all()
    return render(request, 'institutions/manage_institutions.html', {
        'form': form,
        'institutions': institutions
    })


def institution_modal(request, institution_id):
    institution = get_object_or_404(Institution, id=institution_id)
    courses = institution.courses.all()
    stats = {
        'total': institution.applications.count(),
        'approved': institution.applications.filter(status='APPROVED').count(),
        'rejected': institution.applications.filter(status='REJECTED').count(),
        'pending': institution.applications.filter(status='PENDING').count(),
    }
    return render(request, 'institutions/institution_modal.html', {
        'institution': institution,
        'courses': courses,
        'stats': stats
    })



def add_course_modal(request, institution_id):
    institution = get_object_or_404(Institution, id=institution_id)

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.institution = institution
            course.save()
            return JsonResponse({ 'success': True })
        else:
            return JsonResponse({ 'success': False, 'errors': form.errors })


def institution_stats_view(request):
    institution_stats = (
        Application.objects
        .values('institution__name')
        .annotate(
            applicants=Count('id'),
            awarded=Count('id', filter=Q(status='awarded'))
        )
        .order_by('-applicants')
    )
    return render(request, 'institutions/institution_stats.html', {'institution_stats': institution_stats})

