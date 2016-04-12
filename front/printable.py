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

    print top

    header = Paragraph(unidecode(venta.cliente.razon_social.upper()), style)
    w, h = header.wrap(doc.width - 88 * mm, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 19.5 * mm, doc.height + doc.topMargin - top * mm)

    header = Paragraph(venta.cliente.numero_documento, style)
    w, h = header.wrap(doc.width - 88 * mm, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 9.3 * mm, doc.height + doc.topMargin - 34 * mm)

    header = Paragraph(venta.cliente.numero_documento, style)
    w, h = header.wrap(doc.width - 88 * mm, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 9.3 * mm, doc.height + doc.topMargin - 34 * mm)

    header = Paragraph('%s - %s - %s - %s' % (venta.cliente.direccion.upper(), venta.cliente.ciudad.upper(), venta.cliente.distrito.upper(), venta.cliente.departamento.upper()), style)
    w, h = header.wrap(doc.width - 100 * mm, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 17 * mm, doc.height + doc.topMargin - 44 * mm)

    header = Paragraph(venta.fecha_factura.strftime('%d/%m/%Y'), style)
    w, h = header.wrap(doc.width - 88 * mm, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 159.5 * mm, doc.height + doc.topMargin - 26 * mm)

    header = Paragraph(venta.numero_guia, style)
    w, h = header.wrap(doc.width - 88 * mm, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 159.5 * mm, doc.height + doc.topMargin - 42 * mm)

    header = Paragraph(venta.cliente.codcliente.upper(), style)
    w, h = header.wrap(doc.width, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 2.5 * mm, doc.height + doc.topMargin - 56.5 * mm)

    header = Paragraph(venta.orden_compra.upper(), style)
    w, h = header.wrap(doc.width, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 43 * mm, doc.height + doc.topMargin - 56.5 * mm)

    header = Paragraph(venta.condiciones.upper(), style)
    w, h = header.wrap(doc.width, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 71 * mm, doc.height + doc.topMargin - 56.5 * mm)

    try:
      header = Paragraph(venta.vencimiento.strftime('%d/%m/%Y'), style)
      w, h = header.wrap(doc.width, doc.topMargin)
      header.drawOn(canvas, doc.leftMargin + 107 * mm, doc.height + doc.topMargin - 56.5 * mm)
    except:
      print 'NoneType'

    header = Paragraph(venta.hora, style)
    w, h = header.wrap(doc.width, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 137 * mm, doc.height + doc.topMargin - 86.5 * mm)


    footer = Paragraph(cardinal(float(venta.total_venta)).upper(), style)
    w, h = footer.wrap(doc.width, doc.bottomMargin)
    footer.drawOn(canvas, doc.leftMargin + 7.8 * mm, 28.23 * mm)

    subtotal = float(venta.total_venta) / 1.18
    igv = float(venta.total_venta) -  subtotal

    footer = Paragraph('%.2f' % subtotal, styler)
    w, h = footer.wrap(doc.width, doc.bottomMargin)
    footer.drawOn(canvas, doc.leftMargin - 9 * mm, 28 * mm)

    footer = Paragraph('%.2f' % igv, styler)
    w, h = footer.wrap(doc.width, doc.bottomMargin)
    footer.drawOn(canvas, doc.leftMargin - 9 * mm, 22.5 * mm)

    footer = Paragraph('%.2f' % venta.total_venta, styler)
    w, h = footer.wrap(doc.width, doc.bottomMargin)
    footer.drawOn(canvas, doc.leftMargin - 9 * mm, 17.5 * mm)


    canvas.restoreState()

  def imprimir(self, venta):

    buffer = self.buffer
    doc = SimpleDocTemplate(buffer, pagesize = self.pagesize, topMargin = 10.5 * cm, leftMargin = 1 * cm, rightMargin = 1 * cm, bottomMargin = 4 * cm, showBoundary = 0)

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
        the_prod = '%s  %s - %s' % (detalle.lote.producto.producto.upper(), comercial, unidecode(detalle.lote.producto.marca.upper()))

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
          string += ' / VCTO: %s' % detalle.lote.numero
        fila.append(Paragraph(string, stylep))
        fila.append(Spacer(0, 6 *mm))
        tabla.append(fila)


    detalles_tabla = Table(tabla, colWidths = [10 * mm, 12 * mm, 125 *mm, None], style = tabla_requerimiento_estilo_ref(),
        repeatRows = 1)

    elements.append(detalles_tabla)

    doc.build(elements, onFirstPage = partial(self._header_footer, venta = venta),
      onLaterPages = partial(self._header_footer, venta = venta))

    pdf = buffer.getvalue()
    buffer.close()
    return pdf