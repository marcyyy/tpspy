from django.conf.urls import url
from django.urls import path
from django.contrib import admin
from . import views
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse


urlpatterns = [
	path('',views.profile),
	path('login/', LoginView.as_view(template_name='information/login.html'), name="login"),
	path('logout/', LogoutView.as_view(template_name='information/logout.html'), name="logout"),
	path('register/', views.register, name='register'),
	path('profile/', views.profile, name='profile'),
	path('settings/', views.settings, name='settings'),
	path('complaints/', views.complaints, name='complaints'),
	path('complaints_h/', views.complaints_history, name='complaints_h'),
	path('visitors/', views.visitors, name='visitors'),
	path('visitors_h/', views.visitors_history, name='visitors_h'),
	path('billings/', views.billings, name='billings'),
	path('billings_p/', views.billings_p, name='billings_p'),
	path('analytics/', views.analytics, name='analytics'),
	path('settings_pass/', views.settings_pass, name='settings_pass'),
]