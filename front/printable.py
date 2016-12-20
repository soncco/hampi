from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer, PageBreak, NextPageTemplate, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.units import inch, mm, cm
from reportlab.lib import colors

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from unidecode import unidecode

from django.template.defaultfilters import date as _date

from datetime import date, datetime, timedelta
from functools import partial

from numword.numword_es import cardinal

def tabla_requerimiento_estilo_ref():
  return TableStyle(
      [
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Oblique'),
        ('FONTSIZE', (0,0), (-1,-1), 7),
        #('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        #('BOX', (0,0), (-1,-1), 0.25, colors.black),
        ('ALIGNMENT', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGNMENT', (3,-1), (-1,-1), 'RIGHT'),
        ('ALIGNMENT', (4,-1), (-1,-1), 'RIGHT'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
      ]
    )

class ImpresionFactura:
  def __init__(self, buffer, pagesize):
    self.buffer = buffer
    if pagesize == 'A4':
      self.pagesize = A4
    elif pagesize == 'Letter':
      self.pagesize = letter
      self.width, self.height = self.pagesize

  @staticmethod
  def _header_footer(canvas, doc, venta):
    canvas.saveState()

    pdfmetrics.registerFont(TTFont('A1979', 'A1979.ttf'))

    subir = 1.2 * cm

    styles = getSampleStyleSheet()
    style = ParagraphStyle('A1979')
    style.fontName = 'A1979'
    style.fontSize = 7

    styler = ParagraphStyle('A1979R')
    styler.fontName = 'A1979'
    styler.fontSize = 7
    styler.alignment = TA_RIGHT

    razon_social = venta.cliente.razon_social
    if len(razon_social) <= 52:
      top = 26
    else:
      top = 30

    header = Paragraph(unidecode(venta.cliente.razon_social.upper()), style)
    w, h = header.wrap(doc.width - 88 * mm, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 19.5 * mm, doc.height + doc.topMargin - top * mm + subir)

    header = Paragraph(venta.cliente.numero_documento, style)
    w, h = header.wrap(doc.width - 88 * mm, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 9.3 * mm, doc.height + doc.topMargin - 34 * mm + subir)

    header = Paragraph(venta.cliente.numero_documento, style)
    w, h = header.wrap(doc.width - 88 * mm, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 9.3 * mm, doc.height + doc.topMargin - 34 * mm + subir)

    direccion = '%s - %s - %s - %s' % (venta.cliente.direccion.upper(), venta.cliente.ciudad.upper(), venta.cliente.distrito.upper(), venta.cliente.departamento.upper())

    if len(direccion) <= 50:
      top = 40
    else:
      top = 44

    header = Paragraph(direccion, style)
    w, h = header.wrap(doc.width - 100 * mm, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 17 * mm, doc.height + doc.topMargin - top * mm + subir)

    header = Paragraph(venta.fecha_factura.strftime('%d/%m/%Y'), style)
    w, h = header.wrap(doc.width - 88 * mm, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 159.5 * mm, doc.height + doc.topMargin - 26 * mm + subir)

    header = Paragraph(venta.numero_guia, style)
    w, h = header.wrap(doc.width - 88 * mm, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 159.5 * mm, doc.height + doc.topMargin - 42 * mm + subir)

    header = Paragraph(venta.cliente.codcliente.upper(), style)
    w, h = header.wrap(doc.width, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 2.5 * mm, doc.height + doc.topMargin - 56.5 * mm + subir)

    header = Paragraph(venta.orden_compra.upper(), style)
    w, h = header.wrap(doc.width, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 43 * mm, doc.height + doc.topMargin - 56.5 * mm + subir)

    header = Paragraph(venta.condiciones.upper(), style)
    w, h = header.wrap(doc.width, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 71 * mm, doc.height + doc.topMargin - 56.5 * mm + subir)

    try:
      header = Paragraph(venta.vencimiento.strftime('%d/%m/%Y'), style)
      w, h = header.wrap(doc.width, doc.topMargin)
      header.drawOn(canvas, doc.leftMargin + 107 * mm, doc.height + doc.topMargin - 56.5 * mm + subir)
    except:
      print 'NoneType'

    header = Paragraph(venta.hora, style)
    w, h = header.wrap(doc.width, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 137 * mm, doc.height + doc.topMargin - 86.5 * mm + subir)


    subir = 1.2 * cm
    footer = Paragraph(cardinal(float(venta.total_venta)).upper(), style)
    w, h = footer.wrap(doc.width, doc.bottomMargin)
    footer.drawOn(canvas, doc.leftMargin + 7.8 * mm, 28.23 * mm + subir)

    subtotal = float(venta.total_venta) / 1.18
    igv = float(venta.total_venta) -  subtotal

    footer = Paragraph('%.2f' % subtotal, styler)
    w, h = footer.wrap(doc.width, doc.bottomMargin)
    footer.drawOn(canvas, doc.leftMargin - 9 * mm, 30 * mm)

    footer = Paragraph('%.2f' % igv, styler)
    w, h = footer.wrap(doc.width, doc.bottomMargin)
    footer.drawOn(canvas, doc.leftMargin - 9 * mm, 24.5 * mm)

    footer = Paragraph('%.2f' % venta.total_venta, styler)
    w, h = footer.wrap(doc.width, doc.bottomMargin)
    footer.drawOn(canvas, doc.leftMargin - 9 * mm, 19.5 * mm)


    canvas.restoreState()

  def imprimir(self, venta):

    buffer = self.buffer
    doc = SimpleDocTemplate(buffer, pagesize = self.pagesize, topMargin = 10.5 * cm, leftMargin = 1 * cm, rightMargin = 1 * cm, bottomMargin = 4 * cm + 1.2 * cm, showBoundary = 0)

    pdfmetrics.registerFont(TTFont('A1979', 'A1979.ttf'))

    styles = getSampleStyleSheet()
    style = ParagraphStyle('A1979')
    style.fontName = 'A1979'
    style.fontSize = 7

    styler = ParagraphStyle('A1979R')
    styler.fontName = 'A1979'
    styler.fontSize = 7
    styler.alignment = TA_RIGHT

    stylep = ParagraphStyle('A1979P')
    stylep.fontName = 'A1979'
    stylep.fontSize = 7
    stylep.leftIndent = 5

    elements = []

    tabla = []

    for detalle in venta.ventadetalle_set.all():
      fila = []
      #fila.append(Paragraph(detalle.lote.producto.codigo, style))
      fila.append(Paragraph(str(detalle.cantidad), style))
      fila.append(Paragraph(detalle.lote.producto.unidad_medida.upper(), style))

      comercial = detalle.lote.producto.comercial.upper()
      if comercial == '':
        the_prod = '%s - %s' % (detalle.lote.producto.producto.upper(), unidecode(detalle.lote.producto.marca.upper()))
      else:
        the_prod = '%s / %s - %s' % (detalle.lote.producto.producto.upper(), comercial, unidecode(detalle.lote.producto.marca.upper()))

      fila.append(Paragraph(the_prod, style))

      if detalle.precio_unitario != 0:

        fila.append(Paragraph('%.3f' % detalle.precio_unitario, styler))
        fila.append(Paragraph('%.3f' % detalle.total, styler))

      else:

        fila.append(Paragraph("", styler))
        fila.append(Paragraph("", styler))


      tabla.append(fila)

      if detalle.lote.numero or detalle.lote.vencimiento:
        string = ''
        fila = ['', '']
        if detalle.lote.numero:
          string += 'LOTE: %s          ' % detalle.lote.numero
        if detalle.lote.vencimiento:
          string += ' / VCTO: %s' % detalle.lote.vencimiento.strftime('%d/%m/%Y')
        fila.append(Paragraph(string, stylep))
        fila.append(Spacer(0, 1 *mm))
        tabla.append(fila)


    detalles_tabla = Table(tabla, colWidths = [10 * mm, 13 * mm, 125 *mm, None], style = tabla_requerimiento_estilo_ref(),
        repeatRows = 1)

    elements.append(detalles_tabla)

    doc.build(elements, onFirstPage = partial(self._header_footer, venta = venta),
      onLaterPages = partial(self._header_footer, venta = venta))

    pdf = buffer.getvalue()
    buffer.close()
    return pdf


class ImpresionGuia:
  def __init__(self, buffer, pagesize):
    self.buffer = buffer
    if pagesize == 'A4':
      self.pagesize = A4
    elif pagesize == 'Letter':
      self.pagesize = letter
      self.width, self.height = self.pagesize

  @staticmethod
  def _header_footer(canvas, doc, venta):
    canvas.saveState()

    pdfmetrics.registerFont(TTFont('A1979', 'A1979.ttf'))

    subir = 2 * mm
    subirmas = 5 * mm

    styles = getSampleStyleSheet()
    style = ParagraphStyle('A1979')
    style.fontName = 'A1979'
    style.fontSize = 7

    styler = ParagraphStyle('A1979R')
    styler.fontName = 'A1979'
    styler.fontSize = 7
    styler.alignment = TA_RIGHT

    razon_social = venta.cliente.razon_social
    if len(razon_social) <= 52:
      top = 26
    else:
      top = 30

    header = Paragraph(venta.fecha_emision.strftime('%d/%m/%Y'), style)
    w, h = header.wrap(doc.width - 88 * mm, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 25.2 * mm, doc.height + doc.topMargin - 28.5 * mm + subir + subirmas)

    header = Paragraph(venta.fecha_traslado.strftime('%d/%m/%Y'), style)
    w, h = header.wrap(doc.width - 88 * mm, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 78.2 * mm, doc.height + doc.topMargin - 28.5 * mm + subir + subirmas)


    header = Paragraph(venta.condiciones, style)
    w, h = header.wrap(doc.width - 88 * mm, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 4.1 * mm, doc.height + doc.topMargin - 39.8 * mm + subir + subirmas)

    header = Paragraph(venta.orden_compra, style)
    w, h = header.wrap(doc.width - 88 * mm, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 39.2 * mm, doc.height + doc.topMargin - 39.8 * mm + subir + subirmas)

    header = Paragraph(venta.fecha_factura.strftime('%d/%m/%Y'), style)
    w, h = header.wrap(doc.width - 88 * mm, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 74.8 * mm, doc.height + doc.topMargin - 39.8 * mm + subir + subirmas)


    header = Paragraph(venta.procedencia.upper(), style)
    w, h = header.wrap(doc.width - 110 * mm, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 19.6 * mm, doc.height + doc.topMargin - 55.8 * mm + subirmas)

    header = Paragraph(venta.llegada.upper(), style)
    w, h = header.wrap(doc.width - 120 * mm, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 123.4 * mm, doc.height + doc.topMargin - 55.8 * mm + subirmas)


    header = Paragraph(venta.cliente.razon_social.upper(), style)
    w, h = header.wrap(doc.width - 110 * mm, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 16.8 * mm, doc.height + doc.topMargin - 69.6 * mm + subir + subirmas)

    header = Paragraph(venta.cliente.numero_documento, style)
    w, h = header.wrap(doc.width - 110 * mm, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 14.7 * mm, doc.height + doc.topMargin - 76.9 * mm + subir + subirmas)


    # p.drawString(left, top - 10, unidecode(venta.vehiculo.upper()))
    # p.drawString(left, top - 20, unidecode(venta.inscripcion.upper()))
    # p.drawString(left, top - 30, unidecode(venta.licencia.upper()))


    footer = Paragraph('FACTURA', style)
    w, h = footer.wrap(doc.width, doc.bottomMargin)
    footer.drawOn(canvas, doc.leftMargin + 18.2 * mm, 26.5 * mm + subir + subirmas)

    footer = Paragraph(venta.numero_factura, style)
    w, h = footer.wrap(doc.width, doc.bottomMargin)
    footer.drawOn(canvas, doc.leftMargin + 67.6 * mm, 26.5 * mm + subir + subirmas)

    footer = Paragraph(unidecode(venta.transportista.upper()), style)
    w, h = footer.wrap(doc.width, doc.bottomMargin)
    footer.drawOn(canvas, doc.leftMargin + 116.79 * mm, 28.2 * mm + subir + subirmas)

    footer = Paragraph(venta.ruc_transportista, style)
    w, h = footer.wrap(doc.width, doc.bottomMargin)
    footer.drawOn(canvas, doc.leftMargin + 116.79 * mm, 22.5 * mm + subir + subirmas)


    canvas.restoreState()

  def imprimir(self, venta):

    subirmas  = 5 * mm

    buffer = self.buffer
    doc = SimpleDocTemplate(buffer, pagesize = self.pagesize, topMargin = 12.5 * cm - subirmas, leftMargin = 1 * cm, rightMargin = 1 * cm, bottomMargin = 3.5 * cm , showBoundary = 0)

    pdfmetrics.registerFont(TTFont('A1979', 'A1979.ttf'))

    styles = getSampleStyleSheet()
    style = ParagraphStyle('A1979')
    style.fontName = 'A1979'
    style.fontSize = 7

    styler = ParagraphStyle('A1979R')
    styler.fontName = 'A1979'
    styler.fontSize = 7
    styler.alignment = TA_RIGHT

    stylep = ParagraphStyle('A1979P')
    stylep.fontName = 'A1979'
    stylep.fontSize = 7
    stylep.leftIndent = 5

    elements = []

    tabla = []

    for detalle in venta.ventadetalle_set.all():
      fila = []
      fila.append(Paragraph(str(detalle.cantidad), style))
      fila.append(Paragraph(detalle.lote.producto.unidad_medida.upper(), style))

      comercial = detalle.lote.producto.comercial.upper()
      if comercial == '':
        the_prod = '%s - %s' % (detalle.lote.producto.producto.upper(), unidecode(detalle.lote.producto.marca.upper()))
      else:
        the_prod = '%s / %s - %s' % (detalle.lote.producto.producto.upper(), comercial, unidecode(detalle.lote.producto.marca.upper()))

      fila.append(Paragraph(the_prod, style))

      tabla.append(fila)

      if detalle.lote.numero or detalle.lote.vencimiento:
        string = ''
        fila = ['']
        fila.append(Spacer(0, 1 *mm))
        if detalle.lote.numero:
          string += 'LOTE: %s          ' % detalle.lote.numero
        if detalle.lote.vencimiento:
          string += ' / VCTO: %s' % detalle.lote.vencimiento.strftime('%d/%m/%Y')

        fila.append(Paragraph(string, stylep))
        tabla.append(fila)


    detalles_tabla = Table(tabla, colWidths = [10 * mm, 13 * mm, None], style = tabla_requerimiento_estilo_ref(),
        repeatRows = 1)

    elements.append(detalles_tabla)

    doc.build(elements, onFirstPage = partial(self._header_footer, venta = venta),
      onLaterPages = partial(self._header_footer, venta = venta))

    pdf = buffer.getvalue()
    buffer.close()
    return pdf
