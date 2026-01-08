import csv
import os
import re

# Parse date function
def parse_date(date_str):
    if not date_str or '/' not in date_str:
        return None
    parts = date_str.strip().split('/')
    if len(parts) != 3:
        return None
    try:
        p0, p1, p2 = int(parts[0]), int(parts[1]), int(parts[2])
        if p2 < 100:
            p2 = 2000 + p2
        if p2 > 31:  # Year at end
            month, day, year = p0, p1, p2
            return f"{year}-{month:02d}-{day:02d}"
    except:
        pass
    return None

# Parse rupiah
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

# Read CSV
all_data = []
with open('KAS_2026.csv', 'r', encoding='utf-8-sig', errors='ignore') as f:
    reader = csv.reader(f)
    for _ in range(5):  # Skip header
        next(reader, None)
    
    for i, row in enumerate(reader):
        if len(row) < 4:
            continue
        tanggal_str = row[0].strip() if row[0] else ''
        if not tanggal_str or '2026' not in tanggal_str:
            continue
        
        tanggal = parse_date(tanggal_str)
        keterangan = row[1].strip() if len(row) > 1 and row[1] else ''
        debit = parse_rupiah(row[2]) if len(row) > 2 else 0
        kredit = parse_rupiah(row[3]) if len(row) > 3 else 0
        
        all_data.append({
            'tanggal': tanggal,
            'keterangan': keterangan,
            'debit': debit,
            'kredit': kredit
        })

print(f"Total data in CSV: {len(all_data)}")
print("\nData Debit (Uang Masuk) di CSV:")
debit_count = 0
for i, d in enumerate(all_data):
    if d['debit'] > 0:
        debit_count += 1
        print(f"{i+1}. {d['tanggal']} | {d['keterangan'][:50]} | Debit: {d['debit']:,}")

print(f"\nTotal Data Debit: {debit_count}")
