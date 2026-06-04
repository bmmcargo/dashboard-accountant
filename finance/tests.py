from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import date
from finance.models import (
    OpsInbound, InboundTransaction,
    OpsManifest, Manifest,
    OpsOutbound, OutboundTransaction
)

class ExportPDFTestCase(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(username='testuser', password='password')
        
        # Create Inbound Data
        self.inbound_new = OpsInbound.objects.create(
            nomor_resi='RESI-NEW-111',
            tanggal=date(2026, 1, 15),
            pengirim='Pengirim New',
            penerima='Penerima New',
            asal='Jakarta',
            tujuan='Surabaya',
            berat=Decimal('10.50'),
            status='DITERIMA'
        )
        self.inbound_legacy = InboundTransaction.objects.create(
            no_resi='RESI-LEG-222',
            tanggal_masuk_stt=date(2026, 1, 20),
            vendor='Vendor Legacy',
            tujuan='Medan',
            kilo=Decimal('15.00'),
            total_biaya=Decimal('150000')
        )
        
        # Create Manifest Data
        self.manifest_new = OpsManifest.objects.create(
            nomor_manifest='MAN-NEW-333',
            tanggal=date(2026, 1, 25),
            armada='Truck A',
            rute='Jakarta -> Surabaya',
            status='DRAFT'
        )
        self.manifest_legacy = Manifest.objects.create(
            no_resi='MAN-LEG-444',
            tanggal_kirim=date(2026, 1, 28),
            penerima='Ekspedisi B',
            tujuan='Bandung',
            koli=5,
            kg=50.00
        )
        
        # Create Outbound Data
        self.outbound_new = OpsOutbound.objects.create(
            inbound=self.inbound_new,
            manifest=self.manifest_new,
            tanggal=date(2026, 1, 30),
            catatan='Catatan Outbound'
        )
        self.inbound_new.status = 'DIKIRIM'
        self.inbound_new.save()
        
        self.outbound_legacy = OutboundTransaction.objects.create(
            no_resi_bmm='RESI-LEG-OUT-555',
            tanggal=date(2026, 1, 31),
            pengirim='Pengirim Legacy',
            penerima='Penerima Legacy',
            kg='25.0',
            keterangan='Keterangan Legacy'
        )

    def test_export_inbound_pdf_unauthenticated(self):
        url = reverse('export_ops_inbound_pdf')
        response = self.client.get(url)
        # Should redirect to login since it has @login_required
        self.assertEqual(response.status_code, 302)

    def test_export_inbound_pdf_authenticated(self):
        self.client.force_login(self.user)
        url = reverse('export_ops_inbound_pdf')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response.content.startswith(b'%PDF-'))
        
        # Test with filters
        response_filtered = self.client.get(url + '?bulan=1&tahun=2026')
        self.assertEqual(response_filtered.status_code, 200)
        self.assertEqual(response_filtered['Content-Type'], 'application/pdf')

    def test_export_manifest_pdf_authenticated(self):
        self.client.force_login(self.user)
        url = reverse('export_ops_manifest_pdf')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response.content.startswith(b'%PDF-'))
        
        # Test with filters
        response_filtered = self.client.get(url + '?bulan=1&tahun=2026')
        self.assertEqual(response_filtered.status_code, 200)
        self.assertEqual(response_filtered['Content-Type'], 'application/pdf')

    def test_export_outbound_pdf_authenticated(self):
        self.client.force_login(self.user)
        url = reverse('export_ops_outbound_pdf')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response.content.startswith(b'%PDF-'))
        
        # Test with filters
        response_filtered = self.client.get(url + '?bulan=1&tahun=2026')
        self.assertEqual(response_filtered.status_code, 200)
        self.assertEqual(response_filtered['Content-Type'], 'application/pdf')

    def test_export_inbound_excel_authenticated(self):
        self.client.force_login(self.user)
        url = reverse('export_ops_inbound')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    def test_export_manifest_excel_authenticated(self):
        self.client.force_login(self.user)
        url = reverse('export_ops_manifest')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    def test_export_outbound_excel_authenticated(self):
        self.client.force_login(self.user)
        url = reverse('export_ops_outbound')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

