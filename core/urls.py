from django.contrib import admin
from django.urls import path , include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("register/",views.register_view , name="register"),
    path("about/",views.about_view , name="about"),
    path("",views.home_view , name="home"),
    path("how_to/",views.how_to_view , name="how_to"),
    path('contact_us/',views.contact_view , name='contact_us'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
