from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Q, F, Value, DecimalField
from django.db.models.functions import Coalesce
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from decimal import Decimal
from .models import Akun, Jurnal, InboundTransaction, OutboundTransaction
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

# --- INBOUND & OUTBOUND VIEWS ---

@login_required
def inbound_list(request):
    inbound_data = InboundTransaction.objects.all().order_by('-tanggal_masuk_stt')
    
    # Pencarian
    q = request.GET.get('q', '')
    if q:
        inbound_data = inbound_data.filter(
            Q(no_resi__icontains=q) | 
            Q(vendor__icontains=q) | 
            Q(tujuan__icontains=q) |
            Q(keterangan__icontains=q)
        )
    
    # Hitung Total di Summary
    total_kilo = inbound_data.aggregate(Sum('kilo'))['kilo__sum'] or 0
    total_biaya = inbound_data.aggregate(Sum('total_biaya'))['total_biaya__sum'] or 0
    
    context = {
        'inbounds': inbound_data,
        'total_kilo': total_kilo,
        'total_biaya': total_biaya,
        'q': q,
    }
    return render(request, 'finance/inbound_list.html', context)

@login_required
def outbound_list(request):
    outbound_data = OutboundTransaction.objects.all().order_by('-tanggal')
    
    # Pencarian
    q = request.GET.get('q', '')
    if q:
        outbound_data = outbound_data.filter(
            Q(no_resi_bmm__icontains=q) | 
            Q(pengirim__icontains=q) | 
            Q(penerima__icontains=q) |
            Q(keterangan__icontains=q)
        )
    
    # Hitung Total di Summary
    total_pendapatan = outbound_data.aggregate(Sum('total'))['total__sum'] or 0
    total_biaya_vendor = (outbound_data.aggregate(Sum('vendor1_biaya'))['vendor1_biaya__sum'] or 0) + \
                         (outbound_data.aggregate(Sum('vendor2_biaya'))['vendor2_biaya__sum'] or 0)
    total_profit = outbound_data.aggregate(Sum('profit'))['profit__sum'] or 0
    
    context = {
        'outbounds': outbound_data,
        'total_pendapatan': total_pendapatan,
        'total_biaya_vendor': total_biaya_vendor,
        'total_profit': total_profit,
        'q': q,
    }
    return render(request, 'finance/outbound_list.html', context)

# --- INBOUND CRUD ---
from .forms import InboundForm, OutboundForm, ManifestForm

@login_required
def inbound_create(request):
    if request.method == 'POST':
        form = InboundForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Inbound berhasil ditambahkan!')
            return redirect('inbound_list')
    else:
        form = InboundForm()
    return render(request, 'finance/inbound_form.html', {'form': form, 'title': 'Tambah Data Inbound'})

@login_required
def inbound_edit(request, pk):
    inbound = get_object_or_404(InboundTransaction, pk=pk)
    if request.method == 'POST':
        form = InboundForm(request.POST, instance=inbound)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Inbound berhasil diperbarui!')
            return redirect('inbound_list')
    else:
        form = InboundForm(instance=inbound)
    return render(request, 'finance/inbound_form.html', {'form': form, 'title': f'Edit Inbound: {inbound.no_resi}'})

@login_required
def inbound_delete(request, pk):
    inbound = get_object_or_404(InboundTransaction, pk=pk)
    no_resi = inbound.no_resi
    inbound.delete()
    messages.success(request, f'Data Inbound "{no_resi}" berhasil dihapus.')
    return redirect('inbound_list')

# --- OUTBOUND CRUD ---

@login_required
def outbound_create(request):
    if request.method == 'POST':
        form = OutboundForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Outbound berhasil ditambahkan!')
            return redirect('outbound_list')
    else:
        form = OutboundForm()
    return render(request, 'finance/outbound_form.html', {'form': form, 'title': 'Tambah Data Outbound'})

@login_required
def outbound_edit(request, pk):
    outbound = get_object_or_404(OutboundTransaction, pk=pk)
    if request.method == 'POST':
        form = OutboundForm(request.POST, instance=outbound)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Outbound berhasil diperbarui!')
            return redirect('outbound_list')
    else:
        form = OutboundForm(instance=outbound)
    return render(request, 'finance/outbound_form.html', {'form': form, 'title': f'Edit Outbound: {outbound.no_resi_bmm}'})

@login_required
def outbound_delete(request, pk):
    outbound = get_object_or_404(OutboundTransaction, pk=pk)
    no_resi = outbound.no_resi_bmm
    outbound.delete()
    messages.success(request, f'Data Outbound "{no_resi}" berhasil dihapus.')
    return redirect('outbound_list')

# --- MANIFEST VIEWS (Hutang) ---
from .models import Manifest

@login_required
def manifest_list(request):
    # Urutkan berdasarkan tanggal kirim secara Ascending (Kronologis)
    manifest_data = Manifest.objects.all().order_by('tanggal_kirim')
    
    # Filter kategori
    kategori = request.GET.get('kategori', '')
    if kategori:
        manifest_data = manifest_data.filter(kategori=kategori)
    
    # Filter status bayar
    status = request.GET.get('status', '')
    if status == 'lunas':
        manifest_data = manifest_data.filter(status_bayar=True)
    elif status == 'belum':
        manifest_data = manifest_data.filter(status_bayar=False)
    
    # Pencarian
    q = request.GET.get('q', '')
    if q:
        manifest_data = manifest_data.filter(
            Q(no_resi__icontains=q) | 
            Q(pengirim__icontains=q) | 
            Q(penerima__icontains=q) |
            Q(tujuan__icontains=q)
        )
    
    # Hitung Total Hutang
    total_hutang = manifest_data.filter(status_bayar=False).aggregate(Sum('total'))['total__sum'] or 0
    total_lunas = manifest_data.filter(status_bayar=True).aggregate(Sum('total'))['total__sum'] or 0
    
    # Kategori list untuk filter
    kategori_list = Manifest.KATEGORI_CHOICES
    
    context = {
        'manifests': manifest_data,
        'total_hutang': total_hutang,
        'total_lunas': total_lunas,
        'kategori_list': kategori_list,
        'selected_kategori': kategori,
        'selected_status': status,
        'q': q,
    }
    return render(request, 'finance/manifest_list.html', context)

@login_required
def manifest_create(request):
    if request.method == 'POST':
        form = ManifestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Manifest berhasil ditambahkan!')
            return redirect('manifest_list')
    else:
        form = ManifestForm()
    return render(request, 'finance/manifest_form.html', {'form': form, 'title': 'Tambah Manifest'})

@login_required
def manifest_edit(request, pk):
    manifest = get_object_or_404(Manifest, pk=pk)
    if request.method == 'POST':
        form = ManifestForm(request.POST, instance=manifest)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Manifest berhasil diperbarui!')
            return redirect('manifest_list')
    else:
        form = ManifestForm(instance=manifest)
    return render(request, 'finance/manifest_form.html', {'form': form, 'title': f'Edit Manifest: {manifest.no_resi}'})

@login_required
def manifest_delete(request, pk):
    manifest = get_object_or_404(Manifest, pk=pk)
    no_resi = manifest.no_resi
    manifest.delete()
    messages.success(request, f'Data Manifest "{no_resi}" berhasil dihapus.')
    return redirect('manifest_list')
