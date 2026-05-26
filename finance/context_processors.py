"""
Context Processors: Menyediakan data badge notifikasi dan role user untuk sidebar.
Data ini otomatis tersedia di SEMUA template tanpa perlu dipass dari views.
"""
from .models import OpsInbound, OpsManifest
from .decorators import get_user_role


def sidebar_badges(request):
    """
    Hitung jumlah item yang perlu diperhatikan untuk badge notifikasi:
    - Inbound: barang berstatus 'DITERIMA' (belum diproses)
    - Manifest: manifest berstatus 'DRAFT' (belum dikirim)
    - user_role: 'owner' atau 'admin_ops' untuk template logic
    """
    if not request.user.is_authenticated:
        return {}

    inbound_diterima_count = OpsInbound.objects.filter(status='DITERIMA').count()
    manifest_draft_count = OpsManifest.objects.filter(status='DRAFT').count()

    return {
        'badge_inbound': inbound_diterima_count,
        'badge_manifest': manifest_draft_count,
        'user_role': get_user_role(request.user),
    }
