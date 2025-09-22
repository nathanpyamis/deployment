from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
#from .views import set_password_view
app_name = 'applications'

urlpatterns = [
    # Home
    path('', views.home_view, name='home'),

    # Authentication
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('apply/', views.create_application, name='create_application'),
    path('logout/', views.logout_view, name='logout'),



    # Applicant

    path('apply/success/', views.application_success, name='application_success'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    


    # Officer
    path('officer/dashboard/', views.officer_dashboard, name='officer_dashboard'),
    path('officer/student/<int:pk>/', views.officer_view_student_profile, name='officer_view_profile'),
    path('officer/profile/<int:pk>/', views.officer_view_profile, name='officer_view_profile'),
    path('officer/review/<int:pk>/', views.review_application, name='review_application'),

    # PasswordResetView

    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
#   path('set-password/', set_password_view, name='set_password'),

]


