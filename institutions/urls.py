from django.urls import path
from . import views
from .views import institution_stats_view

app_name = 'institutions'

urlpatterns = [
    path('modal/<int:institution_id>/', views.institution_modal, name='institution_modal'),
    path('modal/add-course/<int:institution_id>/', views.add_course_modal, name='add_course_modal'),
    path('institution_stats/', institution_stats_view, name='institution_stats')

]
