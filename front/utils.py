from datetime import datetime

def total_gastos(gastos):
  total = 0
  for gasto in gastos:
    total += gasto.monto

  return total

def total_contados(contados):
  total = 0
  for contado in contados:
    total += contado.total_venta

  return total

def total_amortizacion(amortizaciones):
  total = 0
  for amortizacion in amortizaciones:
    total += amortizacion.monto

  return total

def total_liquidacion(gastos, contados, amortizaciones):
  return amortizaciones + contados - gastos


def diff_dates(date1, date2):
  return abs(date2-date1).days

def grupo_administracion(usuario):
  return usuario.groups.filter(name = 'Administradores')
