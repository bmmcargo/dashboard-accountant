"""
Django Signals: Audit Log otomatis untuk semua model utama.
Mencatat setiap aksi Create, Update, Delete beserta detail perubahan.

NOTE: Signals untuk auto-jurnal (InboundTransaction, Manifest, Cashbon, Penggajian)
sudah ada di models.py. File ini HANYA untuk Audit Log.
"""
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver

from django.contrib.auth.models import User
from .models import (
    Akun, Jurnal, InboundTransaction, OutboundTransaction, Manifest,
    KasHarian, Karyawan, Cashbon, Penggajian, InvoiceTagihan,
    OpsInbound, OpsManifest, OpsOutbound, Penerimaan, AuditLog,
)
from .middleware import get_current_user, get_current_ip


# ============================================================
# HELPER: Mencatat perubahan field (diff lama vs baru)
# ============================================================

def _get_field_changes(instance, old_instance):
    """Bandingkan field instance lama vs baru, return dict perubahan."""
    changes = {}
    for field in instance._meta.fields:
        field_name = field.name
        if field_name in ('id', 'created_at', 'updated_at', 'password'):
            continue
        old_val = getattr(old_instance, field_name, None)
        new_val = getattr(instance, field_name, None)
        if old_val != new_val:
            changes[field_name] = {
                'lama': str(old_val) if old_val is not None else '',
                'baru': str(new_val) if new_val is not None else '',
            }
    return changes


def _get_all_fields(instance):
    """Return semua field sebagai dict untuk log CREATE."""
    data = {}
    for field in instance._meta.fields:
        field_name = field.name
        if field_name in ('id', 'created_at', 'updated_at', 'password'):
            continue
        val = getattr(instance, field_name, None)
        if val is not None:
            data[field_name] = str(val)
    return data


def _create_log(action, instance, changes=None):
    """Helper untuk membuat entry AuditLog dengan Blockchain Hash Chain."""
    user = get_current_user()
    # Skip jika user belum login (misal saat migrate/loaddata)
    if user is None or not hasattr(user, 'pk') or user.is_anonymous:
        user = None

    from django.db import transaction
    from .blockchain import calculate_block_hash
    
    with transaction.atomic():
        # Lock tabel AuditLog untuk mencegah race condition (agar index & hash tidak tabrakan)
        # select_for_update() hanya berjalan kalau ada objek. Kalau kosong tidak bisa.
        last_block = AuditLog.objects.select_for_update().order_by('-block_index', '-id').first()
        
        if last_block:
            new_index = last_block.block_index + 1
            # pastikan last_block punya block_hash, jika belum ada kasih default
            prev_hash = last_block.block_hash if last_block.block_hash else "0" * 64
        else:
            new_index = 1
            prev_hash = "0" * 64

        log = AuditLog(
            block_index=new_index,
            previous_hash=prev_hash,
            user=user,
            model_name=instance.__class__.__name__,
            object_id=str(instance.pk),
            object_repr=str(instance)[:255],
            action=action,
            changes=changes or {},
            ip_address=get_current_ip(),
        )
        
        # Simpan log ke DB untuk men-generate `timestamp` (auto_now_add) dan `id`
        log.save()
        
        # Setelah ada timestamp, hitung hash
        log.block_hash = calculate_block_hash(log)
        
        # Update ulang hash
        log.save(update_fields=['block_hash'])


# ============================================================
# MODEL YANG DI-AUDIT
# ============================================================

AUDITED_MODELS = [
    User, Akun, Jurnal, InboundTransaction, OutboundTransaction, Manifest,
    KasHarian, Karyawan, Cashbon, Penggajian, InvoiceTagihan,
    OpsInbound, OpsManifest, OpsOutbound, Penerimaan,
]


# ============================================================
# PRE_SAVE: Simpan snapshot data lama ke instance._old_instance
# ============================================================

@receiver(pre_save)
def audit_pre_save(sender, instance, **kwargs):
    """Simpan state lama sebelum save untuk perbandingan di post_save."""
    if sender not in AUDITED_MODELS:
        return
    if instance.pk:
        try:
            instance._old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None


# ============================================================
# POST_SAVE: Log CREATE atau UPDATE
# ============================================================

@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    """Catat aksi CREATE atau UPDATE ke AuditLog."""
    if sender not in AUDITED_MODELS:
        return

    if created:
        _create_log('CREATE', instance, {'data': _get_all_fields(instance)})
    else:
        old = getattr(instance, '_old_instance', None)
        if old:
            changes = _get_field_changes(instance, old)
            if changes:  # Hanya log jika ada perubahan nyata
                _create_log('UPDATE', instance, changes)


# ============================================================
# POST_DELETE: Log DELETE
# ============================================================

@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    """Catat aksi DELETE ke AuditLog."""
    if sender not in AUDITED_MODELS:
        return
    _create_log('DELETE', instance, {'data_terhapus': _get_all_fields(instance)})
