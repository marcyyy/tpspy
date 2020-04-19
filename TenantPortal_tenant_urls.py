from django.contrib import admin
from tenant import views
from django.urls import path, include

urlpatterns = [
    path('', views.login_redirect, name='login_redirect'),
    path('admin/', admin.site.urls),
    path('information/', include('information.urls'))
]
