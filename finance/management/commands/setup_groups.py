from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Membuat Group: Owner dan Admin Operasional'

    def handle(self, *args, **options):
        owner_group, created1 = Group.objects.get_or_create(name='Owner')
        if created1:
            self.stdout.write(self.style.SUCCESS('✅ Group "Owner" berhasil dibuat.'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  Group "Owner" sudah ada.'))

        admin_group, created2 = Group.objects.get_or_create(name='Admin Operasional')
        if created2:
            self.stdout.write(self.style.SUCCESS('✅ Group "Admin Operasional" berhasil dibuat.'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  Group "Admin Operasional" sudah ada.'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Selesai! Gunakan Django Admin (/admin/) untuk assign user ke group.'))
        self.stdout.write('  - Owner: Akses penuh (Keuangan + Operasional)')
        self.stdout.write('  - Admin Operasional: Hanya akses Operasional')
