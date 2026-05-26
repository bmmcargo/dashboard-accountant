"""
Django Signals: Audit Log otomatis untuk semua model utama.
Mencatat setiap aksi Create, Update, Delete beserta detail perubahan.

NOTE: Signals untuk auto-jurnal (InboundTransaction, Manifest, Cashbon, Penggajian)
sudah ada di models.py. File ini HANYA untuk Audit Log.
"""
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver

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
        if field_name in ('id', 'created_at', 'updated_at'):
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
        if field_name in ('id', 'created_at', 'updated_at'):
            continue
        val = getattr(instance, field_name, None)
        if val is not None:
            data[field_name] = str(val)
    return data


def _create_log(action, instance, changes=None):
    """Helper untuk membuat entry AuditLog."""
    user = get_current_user()
    # Skip jika user belum login (misal saat migrate/loaddata)
    if user is None or not hasattr(user, 'pk') or user.is_anonymous:
        user = None

    AuditLog.objects.create(
        user=user,
        model_name=instance.__class__.__name__,
        object_id=str(instance.pk),
        object_repr=str(instance)[:255],
        action=action,
        changes=changes or {},
        ip_address=get_current_ip(),
    )


# ============================================================
# MODEL YANG DI-AUDIT
# ============================================================

AUDITED_MODELS = [
    Akun, Jurnal, InboundTransaction, OutboundTransaction, Manifest,
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
