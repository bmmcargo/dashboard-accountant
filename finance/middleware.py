"""
Middleware: Thread-local storage untuk menyimpan current user & IP.
Digunakan oleh Django Signals agar bisa mencatat siapa user yang
melakukan aksi (Create/Update/Delete) di AuditLog.
"""
import threading

_thread_locals = threading.local()


def get_current_user():
    """Ambil user yang sedang login dari thread-local storage."""
    return getattr(_thread_locals, 'user', None)


def get_current_ip():
    """Ambil IP address dari request di thread-local storage."""
    return getattr(_thread_locals, 'ip_address', None)


class CurrentUserMiddleware:
    """
    Middleware yang menyimpan request.user dan IP address ke thread-local.
    Ini memungkinkan Django Signals mengakses info user tanpa menerima request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.user = getattr(request, 'user', None)
        # Ambil IP dari header (support proxy) atau langsung dari REMOTE_ADDR
        _thread_locals.ip_address = (
            request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
            or request.META.get('REMOTE_ADDR')
        )
        response = self.get_response(request)
        return response
