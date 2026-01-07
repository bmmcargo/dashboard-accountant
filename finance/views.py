from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Q, F, Value, DecimalField
from django.db.models.functions import Coalesce
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from decimal import Decimal
from .models import Akun, Jurnal
from .forms import JurnalForm

def get_saldo_akun(akun, start_date=None, end_date=None):
    """Helper to calculate account balance."""
    debit_filter = Q(akun_debit=akun)
    credit_filter = Q(akun_kredit=akun)
    
    if start_date:
        debit_filter &= Q(tanggal__gte=start_date)
        credit_filter &= Q(tanggal__gte=start_date)
    if end_date:
        debit_filter &= Q(tanggal__lte=end_date)
        credit_filter &= Q(tanggal__lte=end_date)
        
    debit = Jurnal.objects.filter(debit_filter).aggregate(
        total=Coalesce(Sum('nominal'), Value(0, output_field=DecimalField()))
    )['total']
    credit = Jurnal.objects.filter(credit_filter).aggregate(
        total=Coalesce(Sum('nominal'), Value(0, output_field=DecimalField()))
    )['total']
    
    if akun.saldo_normal == 'DEBIT':
        return debit - credit
    else:
        return credit - debit

@login_required
def dashboard(request):
    # Summary Cards
    total_aset = 0
    for akun in Akun.objects.filter(kategori='ASSET'):
        total_aset += get_saldo_akun(akun)
        
    total_pendapatan = 0
    for akun in Akun.objects.filter(kategori='REVENUE'):
        total_pendapatan += get_saldo_akun(akun)
        
    total_beban = 0
    for akun in Akun.objects.filter(kategori='EXPENSE'):
        total_beban += get_saldo_akun(akun)
        
    # Perhitungan Pajak 2% (sinkron dengan laporan)
    pajak_2_persen = int(total_pendapatan * Decimal('0.02'))
    laba_bersih = total_pendapatan - pajak_2_persen - total_beban
    
    # Recent Jurnal
    recent_jurnal = Jurnal.objects.all().order_by('-tanggal', '-created_at')[:5]
    
    context = {
        'total_aset': total_aset,
        'total_pendapatan': total_pendapatan,
        'total_beban': total_beban,
        'laba_bersih': laba_bersih,
        'recent_jurnal': recent_jurnal,
    }
    return render(request, 'finance/dashboard.html', context)

@login_required
def jurnal_list(request):
    jurnals = Jurnal.objects.all().order_by('-tanggal', '-created_at')
    
    if request.method == 'POST':
        form = JurnalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Jurnal berhasil ditambahkan!")
            return redirect('jurnal_list')
    else:
        form = JurnalForm()
        
    return render(request, 'finance/jurnal.html', {'jurnals': jurnals, 'form': form})

@login_required
def jurnal_delete(request, pk):
    jurnal = get_object_or_404(Jurnal, pk=pk)
    jurnal.delete()
    messages.success(request, "Data jurnal dihapus.")
    return redirect('jurnal_list')

@login_required
def jurnal_edit(request, pk):
    jurnal = get_object_or_404(Jurnal, pk=pk)
    if request.method == 'POST':
        form = JurnalForm(request.POST, instance=jurnal)
        if form.is_valid():
            form.save()
            messages.success(request, "Jurnal berhasil diperbarui!")
            return redirect('jurnal_list')
    else:
        form = JurnalForm(instance=jurnal)
    return render(request, 'finance/jurnal_edit.html', {'form': form, 'jurnal': jurnal})

@login_required
def buku_besar(request):
    akun_id = request.GET.get('akun')
    selected_akun = None
    transaksi = []
    
    if akun_id:
        selected_akun = get_object_or_404(Akun, id=akun_id)
        # Get all transactions involving this account
        debits = Jurnal.objects.filter(akun_debit=selected_akun).annotate(
            posisi=F('nominal'), # Debit amount
            lawan=F('akun_kredit__nama')
        )
        credits = Jurnal.objects.filter(akun_kredit=selected_akun).annotate(
            posisi=F('nominal'), # Credit amount
            lawan=F('akun_debit__nama')
        )
        
        # Combine manually
        all_events = []
        for d in debits:
            all_events.append({
                'tanggal': d.tanggal,
                'uraian': d.uraian,
                'lawan': d.akun_kredit.nama, # Account on the other side
                'debit': d.nominal,
                'kredit': 0
            })
        for c in credits:
            all_events.append({
                'tanggal': c.tanggal,
                'uraian': c.uraian,
                'lawan': c.akun_debit.nama,
                'debit': 0,
                'kredit': c.nominal
            })
            
        # Sort by date
        all_events.sort(key=lambda x: x['tanggal'])
        
        # Calculate running balance
        saldo = 0
        for event in all_events:
            if selected_akun.saldo_normal == 'DEBIT':
                saldo += event['debit']
                saldo -= event['kredit']
            else:
                saldo += event['kredit']
                saldo -= event['debit']
            event['saldo'] = saldo
            
        transaksi = all_events

    context = {
        'daftar_akun': Akun.objects.all(),
        'selected_akun': selected_akun,
        'transaksi': transaksi
    }
    return render(request, 'finance/buku_besar.html', context)

@login_required
def laporan_keuangan(request):
    # Laba Rugi
    pendapatan = []
    total_pendapatan = 0
    for a in Akun.objects.filter(kategori='REVENUE'):
        s = get_saldo_akun(a)
        if s != 0:
            pendapatan.append({'nama': a.nama, 'nominal': s})
            total_pendapatan += s
            
    beban = []
    total_beban = 0
    for a in Akun.objects.filter(kategori='EXPENSE'):
        s = get_saldo_akun(a)
        if s != 0:
            beban.append({'nama': a.nama, 'nominal': s})
            total_beban += s
            
    laba_rugi_sebelum_pajak = total_pendapatan - total_beban
    
    # Perhitungan Pajak 2% (sesuai format BMM)
    pajak_2_persen = int(total_pendapatan * Decimal('0.02'))  # Pajak 2% dari penghasilan
    laba_kotor = total_pendapatan - pajak_2_persen  # Laba Kotor setelah pajak penghasilan
    biaya_pajak = 0  # Biaya pajak lainnya (bisa diisi jika ada)
    
    # Laba Bersih = Laba Kotor - Total Beban - Biaya Pajak
    laba_rugi = laba_kotor - total_beban - biaya_pajak
    
    # Neraca (Balance Sheet)
    aset = []
    total_aset = 0
    for a in Akun.objects.filter(kategori='ASSET'):
        s = get_saldo_akun(a)
        if s != 0:
            aset.append({'nama': a.nama, 'nominal': s})
            total_aset += s
            
    kewajiban = []
    total_kewajiban = 0
    for a in Akun.objects.filter(kategori='LIABILITY'):
        s = get_saldo_akun(a)
        if s != 0:
            kewajiban.append({'nama': a.nama, 'nominal': s})
            total_kewajiban += s
            
    modal_items = [] # Avoid Variable Clash
    total_modal_awal = 0
    
    for a in Akun.objects.filter(kategori='EQUITY'):
        s = get_saldo_akun(a)
        modal_items.append({'nama': a.nama, 'nominal': s})
        total_modal_awal += s
        
    # Saldo Laba (Retained Earnings) = Laba Rugi
    total_ekuitas = total_modal_awal + laba_rugi
    
    # Checks
    balance_check = total_aset - (total_kewajiban + total_ekuitas)
    
    # Neraca Saldo (Trial Balance)
    neraca_saldo = []
    total_ns_debit = 0
    total_ns_kredit = 0
    
    for a in Akun.objects.all().order_by('kode'):
        saldo = get_saldo_akun(a)
        if saldo != 0:
            ns_debit = 0
            ns_kredit = 0
            if a.saldo_normal == 'DEBIT':
                if saldo >= 0:
                    ns_debit = saldo
                else:
                    ns_kredit = abs(saldo) # Abnormal balance
            else: # CREDIT
                if saldo >= 0:
                    ns_kredit = saldo
                else:
                    ns_debit = abs(saldo) # Abnormal balance
                    
            neraca_saldo.append({
                'kode': a.kode,
                'nama': a.nama,
                'debit': ns_debit,
                'kredit': ns_kredit
            })
            total_ns_debit += ns_debit
            total_ns_kredit += ns_kredit

    # Laporan Arus Kas (Metode Langsung Sederhana)
    arus_kas_masuk = []
    arus_kas_keluar = []
    total_ak_masuk = 0
    total_ak_keluar = 0
    
    # Asumsi akun Kas/Bank mengandung kata 'Kas' atau 'Bank'
    cash_accounts = Akun.objects.filter(Q(nama__icontains='Kas') | Q(nama__icontains='Bank'))
    
    # Pemasukan (Debit di Akun Kas)
    inflows = Jurnal.objects.filter(akun_debit__in=cash_accounts).select_related('akun_kredit').order_by('tanggal')
    for tx in inflows:
        arus_kas_masuk.append({
            'tanggal': tx.tanggal,
            'keterangan': f"Terima dari {tx.akun_kredit.nama} - {tx.uraian}",
            'nominal': tx.nominal
        })
        total_ak_masuk += tx.nominal
        
    # Pengeluaran (Kredit di Akun Kas)
    outflows = Jurnal.objects.filter(akun_kredit__in=cash_accounts).select_related('akun_debit').order_by('tanggal')
    for tx in outflows:
        arus_kas_keluar.append({
            'tanggal': tx.tanggal,
            'keterangan': f"Bayar ke {tx.akun_debit.nama} - {tx.uraian}",
            'nominal': tx.nominal
        })
        total_ak_keluar += tx.nominal
    
    net_cash_flow = total_ak_masuk - total_ak_keluar

    context = {
        'pendapatan': pendapatan, 'total_pendapatan': total_pendapatan,
        'beban': beban, 'total_beban': total_beban,
        'pajak_2_persen': pajak_2_persen, 'laba_kotor': laba_kotor,
        'biaya_pajak': biaya_pajak, 'laba_rugi': laba_rugi,
        'aset': aset, 'total_aset': total_aset,
        'kewajiban': kewajiban, 'total_kewajiban': total_kewajiban,
        'modal': modal_items, 'total_modal': total_modal_awal, 'total_ekuitas': total_ekuitas,
        'balance_check': balance_check,
        'neraca_saldo': neraca_saldo, 'total_ns_debit': total_ns_debit, 'total_ns_kredit': total_ns_kredit,
        'arus_kas_masuk': arus_kas_masuk, 'arus_kas_keluar': arus_kas_keluar,
        'total_ak_masuk': total_ak_masuk, 'total_ak_keluar': total_ak_keluar,
        'net_cash_flow': net_cash_flow
    }
    return render(request, 'finance/laporan.html', context)

# --- Akun (Master Data) Views ---
from .forms import AkunForm

@login_required
def akun_list(request):
    akuns = Akun.objects.all().order_by('kode')
    return render(request, 'finance/akun_list.html', {'akuns': akuns})

@login_required
def akun_create(request):
    if request.method == 'POST':
        form = AkunForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Akun berhasil ditambahkan!')
            return redirect('akun_list')
    else:
        form = AkunForm()
    return render(request, 'finance/akun_form.html', {'form': form, 'title': 'Tambah Akun Baru'})

@login_required
def akun_update(request, pk):
    akun = get_object_or_404(Akun, pk=pk)
    if request.method == 'POST':
        form = AkunForm(request.POST, instance=akun)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data akun diperbarui.')
            return redirect('akun_list')
    else:
        form = AkunForm(instance=akun)
    return render(request, 'finance/akun_form.html', {'form': form, 'title': f'Edit Akun: {akun.nama}'})

@login_required
def akun_delete(request, pk):
    akun = get_object_or_404(Akun, pk=pk)
    try:
        akun.delete()
        messages.success(request, 'Akun berhasil dihapus.')
    except:
        messages.error(request, 'Gagal menghapus akun. Mungkin akun ini sudah dipakai di transaksi.')
    return redirect('akun_list')
