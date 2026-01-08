import csv
import re

def parse_rupiah(val):
    if not val:
        return 0
    val = re.sub(r'[Rp\s",]', '', str(val).strip())
    if not val or val == '-':
        return 0
    try:
        return int(float(val))
    except:
        return 0

print("DATA DEBIT DI CSV:")
print("-" * 50)
with open('KAS_2026.csv', 'r', encoding='utf-8-sig', errors='ignore') as f:
    reader = csv.reader(f)
    for _ in range(5):
        next(reader, None)
    
    for i, row in enumerate(reader):
        if len(row) < 3:
            continue
        
        # Cek kolom DEBIT (index 2)
        debit_str = row[2] if len(row) > 2 else ""
        debit = parse_rupiah(debit_str)
        
        if debit > 0:
            print(f"Row {i+6}: {row[0]} | {row[1]} | {debit}")
