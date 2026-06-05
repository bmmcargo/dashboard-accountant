import hashlib
import json
from django.utils.timezone import localtime

def generate_hash(data_string):
    """Generate SHA-256 hash dari string."""
    return hashlib.sha256(data_string.encode('utf-8')).hexdigest()

def calculate_block_hash(audit_log):
    """
    Hitung hash block berdasarkan data-data di dalam audit_log:
    block_index, previous_hash, timestamp, user_id, action, model_name, object_id, changes
    """
    # Pastikan data changes deterministik (terurut)
    changes_str = json.dumps(audit_log.changes, sort_keys=True)
    
    # Format timestamp yang konsisten
    time_str = audit_log.timestamp.isoformat() if audit_log.timestamp else ""
    user_id = str(audit_log.user_id) if audit_log.user_id else "None"
    
    raw_data = f"{audit_log.block_index}|{audit_log.previous_hash}|{time_str}|{user_id}|{audit_log.action}|{audit_log.model_name}|{audit_log.object_id}|{changes_str}"
    
    return generate_hash(raw_data)

def verify_blockchain_integrity():
    """
    Memeriksa seluruh rantai blok dalam tabel AuditLog dari awal sampai akhir.
    Mengembalikan dict status integritas.
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
