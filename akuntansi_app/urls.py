from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

def custom_login_redirect(request):
    """
    Redirect users based on their groups:
    - Superuser or 'Owner' group -> Dashboard Keuangan
    - 'Admin Operasional' group -> Dashboard Operasional
    """
    if request.user.is_superuser or request.user.groups.filter(name='Owner').exists():
        return redirect('dashboard')
    elif request.user.groups.filter(name='Admin Operasional').exists():
        return redirect('dashboard_ops')
    return redirect('dashboard')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Ganti Password
    path('pengaturan/password/', auth_views.PasswordChangeView.as_view(
        template_name='registration/change_password.html',
        success_url='/'
    ), name='password_change'),
    
    path('custom_login_redirect/', custom_login_redirect, name='custom_login_redirect'),
    path('', include('finance.urls')),
]
