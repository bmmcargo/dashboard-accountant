"""
Decorators & Helpers: Kontrol akses berbasis role (RBAC).

Role yang tersedia:
- Owner (Finance & Atasan): Akses penuh ke seluruh sistem
- Admin Operasional: Hanya akses Inbound dan Manifest
"""
from django.shortcuts import render
from functools import wraps


def owner_required(view_func):
    """
    Decorator: Hanya user dalam group 'Owner' yang boleh mengakses.
    Admin Operasional yang mencoba mengakses URL keuangan akan ditolak (403).
    Superuser otomatis diizinkan.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user

        # Superuser selalu diizinkan
        if user.is_superuser:
            return view_func(request, *args, **kwargs)

        # Cek apakah user masuk group 'Owner'
        if user.groups.filter(name='Owner').exists():
            return view_func(request, *args, **kwargs)

        # Jika bukan Owner → Tolak akses
        return render(request, 'finance/403.html', status=403)

    return _wrapped_view


def is_owner(user):
    """Helper: Cek apakah user adalah Owner atau Superuser."""
    if user.is_superuser:
        return True
    return user.groups.filter(name='Owner').exists()


def is_admin_operasional(user):
    """Helper: Cek apakah user adalah Admin Operasional."""
    return user.groups.filter(name='Admin Operasional').exists()


def admin_or_owner_required(view_func):
    """
    Decorator: Hanya user dalam group 'Owner' ATAU 'Admin Operasional' yang boleh akses.
    User tanpa group assignment akan ditolak (403).
    Superuser otomatis diizinkan.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user

        if user.is_superuser:
            return view_func(request, *args, **kwargs)

        if user.groups.filter(name__in=['Owner', 'Admin Operasional']).exists():
            return view_func(request, *args, **kwargs)

        return render(request, 'finance/403.html', status=403)

    return _wrapped_view


def get_user_role(user):
    """
    Helper: Return role string untuk template context.
    Digunakan oleh context processor dan template sidebar.
    """
    if user.is_superuser or user.groups.filter(name='Owner').exists():
        return 'owner'
    elif user.groups.filter(name='Admin Operasional').exists():
        return 'admin_ops'
    return 'unknown'
