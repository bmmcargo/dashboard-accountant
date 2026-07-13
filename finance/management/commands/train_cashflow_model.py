from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Training model Random Forest untuk prediksi arus kas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--quiet', action='store_true',
            help='Minimal output',
        )

    def handle(self, *args, **options):
        verbose = not options['quiet']

        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write('🤖 TRAINING MODEL PREDIKSI ARUS KAS')
        self.stdout.write('   Random Forest Regression + Moving Average Benchmark')
        self.stdout.write('=' * 60)
        self.stdout.write('')

        try:
            from finance.ml.model_training import full_training_pipeline

            result = full_training_pipeline(verbose=verbose)

            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('=' * 60))
            self.stdout.write(self.style.SUCCESS('✅ TRAINING SELESAI!'))
            self.stdout.write(self.style.SUCCESS('=' * 60))
            self.stdout.write('')
            self.stdout.write('Buka halaman Prediksi Arus Kas di dashboard untuk melihat hasilnya.')
            self.stdout.write('URL: /prediksi/')

        except ValueError as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error: {e}'))
            self.stdout.write(self.style.WARNING(
                '\nTips: Jalankan "python manage.py seed_historical_data" '
                'untuk menambahkan data historis terlebih dahulu.'
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error tak terduga: {e}'))
            import traceback
            traceback.print_exc()
