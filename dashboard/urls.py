
from django.contrib import admin
from django.urls import path , include
from . import views
from django.conf import settings
from django.conf.urls.static import static


app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('sessions/', views.my_sessions, name='my_sessions'),
    path('uploads/', views.uploaded_items, name='uploaded_items'),
    path('analytics/', views.analytics, name='analytics'),
    path("category/",views.category_view , name="category"),
    
    path("interview_requirements/",views.interview_requirements_view , name="interview_requirements"),
    path("presentation_requirements/",views.presentation_requirements_view , name="presentation_requirements"),
    path("communication_requirements/",views.communication_requirements_view , name="communication_requirements"),
    path("question_requirements/",views.question_requirements_view , name="question_requirements"),
    
    path("profile/",views.profile_view, name="profile"),
    path("profile_edit/",views.profile_edit_view, name="profile_edit"), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


