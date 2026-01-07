from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Ganti Password
    path('pengaturan/password/', auth_views.PasswordChangeView.as_view(
        template_name='registration/change_password.html',
        success_url='/'
    ), name='password_change'),
    
    path('', include('finance.urls')),
]
