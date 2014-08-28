def total_amortizaciones(deuda):
  total_amortizacion = 0
  for amortizacion in deuda.amortizacion_set.all():
    total_amortizacion += amortizacion.monto

  return total_amortizacion

def saldo_deuda(deuda):
  return deuda.registro_padre.total_venta - total_amortizaciones(deuda)
