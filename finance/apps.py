from django.apps import AppConfig


class FinanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'finance'
    verbose_name = 'Sistem Akuntansi BMM Cargo'

    def ready(self):
        """Import signals saat app sudah siap agar audit log aktif."""
        import finance.signals  # noqa: F401
