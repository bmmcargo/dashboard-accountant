from django import template

register = template.Library()

def terbilang_satuan(n):
    """Convert single digit to Indonesian word."""
    satuan = ['', 'Satu', 'Dua', 'Tiga', 'Empat', 'Lima', 'Enam', 'Tujuh', 'Delapan', 'Sembilan', 'Sepuluh', 'Sebelas']
    return satuan[n] if n < 12 else ''

def terbilang_helper(n):
    """Recursive helper to convert number to Indonesian words."""
    if n < 0:
        return 'Minus ' + terbilang_helper(-n)
    elif n == 0:
        return ''
    elif n < 12:
        return terbilang_satuan(n)
    elif n < 20:
        return terbilang_satuan(n - 10) + ' Belas'
    elif n < 100:
        return terbilang_satuan(n // 10) + ' Puluh ' + terbilang_helper(n % 10)
    elif n < 200:
        return 'Seratus ' + terbilang_helper(n % 100)
    elif n < 1000:
        return terbilang_satuan(n // 100) + ' Ratus ' + terbilang_helper(n % 100)
    elif n < 2000:
        return 'Seribu ' + terbilang_helper(n % 1000)
    elif n < 1000000:
        return terbilang_helper(n // 1000) + ' Ribu ' + terbilang_helper(n % 1000)
    elif n < 1000000000:
        return terbilang_helper(n // 1000000) + ' Juta ' + terbilang_helper(n % 1000000)
    elif n < 1000000000000:
        return terbilang_helper(n // 1000000000) + ' Miliar ' + terbilang_helper(n % 1000000000)
    else:
        return terbilang_helper(n // 1000000000000) + ' Triliun ' + terbilang_helper(n % 1000000000000)

@register.filter(name='terbilang')
def terbilang(value):
    """
    Django template filter to convert number to Indonesian words.
    Usage: {{ invoice.total|terbilang }}
    Output: "Satu Juta Lima Ratus Ribu Rupiah"
    """
    try:
        # Convert to integer (remove decimals)
        n = int(value)
        if n == 0:
            return 'Nol Rupiah'
        
        result = terbilang_helper(n).strip()
        # Clean up extra spaces
        result = ' '.join(result.split())
        return result + ' Rupiah'
    except (ValueError, TypeError):
        return str(value)
