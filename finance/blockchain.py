import hashlib
import hmac
import json
from django.conf import settings

def generate_hash(data_string):
    """Generate SHA-256 hash dari string (dipakai untuk certificate backup)."""
    return hashlib.sha256(data_string.encode('utf-8')).hexdigest()

def calculate_block_hash(audit_log):
    """
    Hitung HMAC-SHA256 block hash menggunakan Django SECRET_KEY sebagai kunci.
    HMAC memastikan hash hanya bisa diverifikasi oleh server yang tahu SECRET_KEY,
    sehingga attacker dengan akses DB tidak bisa merekalkukasi ulang chain.
    """
    changes_str = json.dumps(audit_log.changes, sort_keys=True)
    time_str = audit_log.timestamp.isoformat() if audit_log.timestamp else ""
    user_id = str(audit_log.user_id) if audit_log.user_id else "None"

    raw_data = (
        f"{audit_log.block_index}|{audit_log.previous_hash}|{time_str}|"
        f"{user_id}|{audit_log.action}|{audit_log.model_name}|"
        f"{audit_log.object_id}|{changes_str}"
    )

    return hmac.new(
        settings.SECRET_KEY.encode('utf-8'),
        raw_data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

def verify_blockchain_integrity():
    """
    Memeriksa seluruh rantai blok dalam tabel AuditLog dari awal sampai akhir.
    Mengembalikan dict status integritas.

    Kompleksitas O(N) — untuk deployment produksi dengan > 50.000 blok,
    pertimbangkan implementasi periodic checkpointing.
    """
    from .models import AuditLog
    
    logs = AuditLog.objects.all().order_by('block_index', 'timestamp')
    
    if not logs.exists():
        return {"is_valid": True, "total_blocks": 0, "message": "No blocks found"}

    previous_hash = "0" * 64
    expected_index = 1
    
    for log in logs:
        # Cek urutan index
        if log.block_index != expected_index:
            return {
                "is_valid": False, 
                "broken_block": log.id,
                "message": f"Block index mismatch at block {log.block_index}. Expected {expected_index}."
            }
            
        # Cek linkage
        if log.previous_hash != previous_hash:
            return {
                "is_valid": False, 
                "broken_block": log.id,
                "message": f"Previous hash mismatch at block {log.block_index}."
            }
            
        # Cek hash integrity
        calculated_hash = calculate_block_hash(log)
        if log.block_hash != calculated_hash:
            return {
                "is_valid": False,
                "broken_block": log.id,
                "message": f"Hash integrity failed at block {log.block_index}. Data was tampered."
            }
            
        previous_hash = log.block_hash
        expected_index += 1
        
    return {
        "is_valid": True,
        "total_blocks": logs.count(),
        "message": "Blockchain is valid and verified."
    }

def get_tampered_block_ids():
    """
    Scan seluruh chain dan kembalikan set berisi ID AuditLog yang terdeteksi manipulasi.
    Berbeda dengan verify_blockchain_integrity(), fungsi ini TIDAK berhenti di blok pertama —
    ia terus berjalan untuk menemukan SEMUA blok yang bermasalah.

    Sebuah blok ditandai 'tampered' jika:
    - block_hash tidak cocok dengan hasil kalkulasi ulang (data block diubah langsung di DB), ATAU
    - previous_hash tidak cocok dengan block_hash blok sebelumnya (chain linkage putus).
    """
    from .models import AuditLog

    logs = AuditLog.objects.all().order_by('block_index', 'timestamp')
    tampered = set()
    prev_hash_map = {}  # block_index -> actual stored block_hash

    for log in logs:
        # Cek 1: data integrity (apakah block_hash masih valid?)
        recalculated = calculate_block_hash(log)
        data_tampered = (log.block_hash != recalculated)

        # Cek 2: chain linkage (apakah previous_hash menunjuk ke blok sebelumnya yang benar?)
        expected_prev = prev_hash_map.get(log.block_index - 1, "0" * 64)
        chain_broken = (log.previous_hash != expected_prev)

        if data_tampered or chain_broken:
            tampered.add(log.id)

        prev_hash_map[log.block_index] = log.block_hash

    return tampered


def migrate_existing_logs_to_blockchain():
    """
    Fungsi utilitas untuk dijalankan sekali guna mengonversi
    AuditLog lama yang belum punya block_hash menjadi format Blockchain.
    """
    from .models import AuditLog
    
    logs = AuditLog.objects.all().order_by('timestamp')
    
    previous_hash = "0" * 64
    block_index = 1
    
    for log in logs:
        log.block_index = block_index
        log.previous_hash = previous_hash
        
        # Calculate new hash
        new_hash = calculate_block_hash(log)
        log.block_hash = new_hash
        
        # Simpan tanpa men-trigger signal tambahan
        AuditLog.objects.filter(pk=log.pk).update(
            block_index=block_index,
            previous_hash=previous_hash,
            block_hash=new_hash
        )
        
        previous_hash = new_hash
        block_index += 1
