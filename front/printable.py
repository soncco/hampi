# -*- coding: utf-8 -*-

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


class ImpresionAnexo:
  def __init__(self, buffer, pagesize):
    self.buffer = buffer
    if pagesize == 'A4':
      self.pagesize = landscape(A4)
    elif pagesize == 'Letter':
      self.pagesize = landscape(letter)
      self.width, self.height = self.pagesize

  @staticmethod
  def _header_footer(canvas, doc, entrada):
    canvas.saveState()

    canvas.restoreState()

  def imprimir(self, entrada):

    def normal_custom(size):
      return ParagraphStyle(
          name = 'normal_custom_%s' % str(size),
          fontName = 'Helvetica',
          fontSize = size,
      )

    def negrita_custom(size):
      return ParagraphStyle(
          name = 'negrita_custom_%s' % str(size),
          fontName = 'Helvetica-Bold',
          fontSize = size,
      )
    def negrita_custom(size, center = None):
      if center is None:
        return ParagraphStyle(
            name = 'negrita_custom_%s' % str(size),
            fontName = 'Helvetica-Bold',
            fontSize = size,
        )
      else:
        return ParagraphStyle(
            name = 'negrita_custom_%s' % str(size),
            fontName = 'Helvetica-Bold',
            fontSize = size,
            alignment = TA_CENTER
        )

    def tabla_1():
      return TableStyle(
        [
          ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
          ('BOX', (0,0), (-1,-1), 0.25, colors.black),
          ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
          #('SPAN', (0,), (5,total + 2)),
        ]
    )

    def tabla_2():
      return TableStyle(
        [
          ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
          ('BOX', (0,0), (-1,-1), 0.25, colors.black),
          ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
          ('SPAN', (0,0), (0,2)),
          ('SPAN', (1,0), (3,1)),
          ('SPAN', (4,0), (5,1)),
          ('SPAN', (6,0), (7,1)),
          ('SPAN', (8,0), (9,1)),
          ('SPAN', (10,0), (15,0)),
          ('SPAN', (10,1), (11,1)),
          ('SPAN', (12,1), (13,1)),
          ('SPAN', (14,1), (15,1)),
        ]
    )

    buffer = self.buffer
    doc = SimpleDocTemplate(buffer, pagesize = self.pagesize, topMargin = 10 * mm, leftMargin = 10 * mm, rightMargin = 10 * mm, bottomMargin = 10 * mm , showBoundary = 0)


    elements = []

    p = Paragraph(u'DROGUERÍA HAMPI KALLPA EIRL', negrita_custom(15, 1))
    elements.append(p)
    elements.append(Spacer(1, 3 * mm))

    p = Paragraph(u'N° 01', negrita_custom(12, 1))
    elements.append(p)
    elements.append(Spacer(1, 1 * mm))

    p = Paragraph(u'DROGUERIA HAMPI KALLPA EIRL', negrita_custom(10, 1))
    elements.append(p)
    elements.append(Spacer(1, 1 * mm))

    p = Paragraph(u'REGISTRO DE RECEPCION Y CONFORMIDAD', negrita_custom(10, 1))
    elements.append(p)
    elements.append(Spacer(1, 4 * mm))

    p = Paragraph(u'<strong>Fecha</strong>: %s - <strong>Hora</strong>: %s' % (entrada.fecha.strftime('%d/%m/%Y'), entrada.hora_entrada), normal_custom(8))
    elements.append(p)
    elements.append(Spacer(1, 1 * mm))

    p = Paragraph(u'<strong>Q.F.</strong>: Director Técnico: QF Joel Alvarez Ochoa', normal_custom(8))
    elements.append(p)
    elements.append(Spacer(1, 1 * mm))

    p = Paragraph(u'<strong>Proveedor</strong>: %s' % (entrada.proveedor.razon_social), normal_custom(8))
    elements.append(p)
    elements.append(Spacer(1, 1 * mm))

    p = Paragraph(u'<strong>Factura Nro</strong>: %s - <strong>Fecha de Factura</strong>: %s' % (entrada.numero_factura, entrada.fecha_factura.strftime('%d/%m/%Y')), normal_custom(8))
    elements.append(p)
    elements.append(Spacer(1, 1 * mm))

    p = Paragraph(u'<strong>Guía de Remisión Nro</strong>: %s - <strong>Fecha Guía de Remisión</strong>: %s' % (entrada.numero_guia, entrada.fecha_guia.strftime('%d/%m/%Y')), normal_custom(8))
    elements.append(p)
    elements.append(Spacer(1, 1 * mm))

    detalles_data = [
     [Paragraph(u'Cant. Sol.', negrita_custom(8,1)), Paragraph(u'Producto.', negrita_custom(8,1)), Paragraph(u'Presentación', negrita_custom(8,1)), Paragraph(u'F/V', negrita_custom(8,1)), Paragraph(u'Lote', negrita_custom(8,1)), Paragraph(u'Fabricante', negrita_custom(8,1)), Paragraph(u'Cant. Rec.', negrita_custom(8,1)), Paragraph(u'N° Reg. San.', negrita_custom(8,1)), Paragraph(u'F.V. Reg. San.', negrita_custom(8,1)), Paragraph(u'Condiciones de almacenamiento', negrita_custom(8,1))]
    ]

    for detalle in entrada.entradadetalle_set.all():
      comercial = detalle.lote.producto.comercial.upper()
      if comercial == '':
        the_prod = '%s' % (detalle.lote.producto.producto)
      else:
        the_prod = '%s / %s' % (detalle.lote.producto.producto, comercial)

      cantidad = Paragraph(str(detalle.cantidad), normal_custom(8))
      producto = Paragraph(the_prod, normal_custom(8))
      presentacion = ''
      try:
        vencimiento = Paragraph(detalle.lote.vencimiento.strftime('%d/%m/%Y'), normal_custom(8))
      except:
        vencimiento = ''
      lote = Paragraph(detalle.lote.numero, normal_custom(8))
      fabricante = Paragraph(detalle.lote.producto.marca, normal_custom(8))
      nrs = Paragraph(detalle.lote.nrs, normal_custom(8))
      vrs = Paragraph(detalle.lote.vrs, normal_custom(8))
      condiciones = ''


      detalles_data.append(
        [cantidad, producto, presentacion, vencimiento, lote, fabricante, cantidad, nrs, vrs, condiciones]
      )



    detalles_tabla = Table(detalles_data, colWidths = [10 * mm, 80 * mm, 40 * mm, 18 * mm, 18 * mm, None, 10 * mm, None], style=tabla_1())

    elements.append(detalles_tabla)
    elements.append(Spacer(1, 5 * mm))


    p = Paragraph(u'<strong>Entrega</strong>: %s - <strong>Recibe</strong>: %s' % (u'Proveedor o Transportista', u'Q.F. Director Técnico'), normal_custom(8))
    elements.append(p)

    elements.append(PageBreak())

    # Anexo 2.

    p = Paragraph(u'DROGUERÍA HAMPI KALLPA EIRL', negrita_custom(15, 1))
    elements.append(p)
    elements.append(Spacer(1, 3 * mm))

    p = Paragraph(u'ANEXO N° 02', negrita_custom(12, 1))
    elements.append(p)
    elements.append(Spacer(1, 1 * mm))

    p = Paragraph(u'ACTA DE EVALUACIÓN ORGANOLÉPTICA PARA EL INGRESO DE DISPOSITIVOS MÉDICOS AL ALMACÉN DE LA', negrita_custom(10, 1))
    elements.append(p)
    elements.append(Spacer(1, 1 * mm))

    p = Paragraph(u'DROGUERIA HAMPI KALLPA EIRL', negrita_custom(10, 1))
    elements.append(p)
    elements.append(Spacer(1, 1 * mm))

    p = Paragraph(u'<strong>Fecha</strong>: %s' % (entrada.fecha.strftime('%d/%m/%Y')), normal_custom(8))
    elements.append(p)
    elements.append(Spacer(1, 1 * mm))

    p = Paragraph(u'<strong>Factura Nro</strong>: %s - <strong>Guía de Remisión</strong>: %s - <strong>Proveedor</strong>: %s' % (entrada.numero_factura, entrada.numero_guia, entrada.proveedor.razon_social), normal_custom(8))
    elements.append(p)
    elements.append(Spacer(1, 1 * mm))

    detalles_data = [
      [Paragraph(u'N°', negrita_custom(8,1)), Paragraph(u'Producto', negrita_custom(8,1)), '', '', Paragraph(u'Documentos Si(S)- No(N)', negrita_custom(8,1)), '', Paragraph(u'Embalaje adecuado', negrita_custom(8,1)), '', Paragraph(u'Envase inmediato adecuado', negrita_custom(8,1)), '', Paragraph(u'Envase Inmediato', negrita_custom(8,1)), '', ''],
      ['', '', '', '', '', '', '', '', '', '', Paragraph(u'Rotulado adecuado', negrita_custom(8,1)), '', Paragraph(u'Aspecto normal', negrita_custom(8,1)), '', Paragraph(u'Cuerpos extraños', negrita_custom(8,1)), ''],
      ['', Paragraph(u'Descripción', negrita_custom(8,1)), Paragraph(u'Lote', negrita_custom(8,1)), Paragraph(u'FV', negrita_custom(8,1)), Paragraph(u'RS', negrita_custom(8,1)), Paragraph(u'Protocólo Análisis', negrita_custom(8,1)), Paragraph(u'Si', negrita_custom(8,1)), Paragraph(u'No', negrita_custom(8,1)), Paragraph(u'Si', negrita_custom(8,1)), Paragraph(u'No', negrita_custom(8,1)), Paragraph(u'Si', negrita_custom(8,1)), Paragraph(u'No', negrita_custom(8,1)), Paragraph(u'Si', negrita_custom(8,1)), Paragraph(u'No', negrita_custom(8,1)), Paragraph(u'Si', negrita_custom(8,1)), Paragraph(u'No', negrita_custom(8,1))]
    ]

    k = 1
    for detalle in entrada.entradadetalle_set.all():
      comercial = detalle.lote.producto.comercial.upper()
      if comercial == '':
        the_prod = '%s' % (detalle.lote.producto.producto)
      else:
        the_prod = '%s / %s' % (detalle.lote.producto.producto, comercial)


      numero = Paragraph(str(k), normal_custom(8))
      producto = Paragraph(the_prod, normal_custom(8))
      lote = Paragraph(detalle.lote.numero, normal_custom(8))
      try:
        vencimiento = Paragraph(detalle.lote.vencimiento.strftime('%d/%m/%Y'), normal_custom(8))
      except:
        vencimiento = ''
      nrs = Paragraph(detalle.lote.nrs, normal_custom(8))
      k += 1

      detalles_data.append(
        [numero, producto, lote, vencimiento, nrs]
      )
      

    detalles_tabla = Table(detalles_data, colWidths = [6 * mm, 55 * mm, 15 * mm, 18 * mm, 18 * mm, 15 * mm], style= tabla_2())

    elements.append(detalles_tabla)
    elements.append(Spacer(1, 5 * mm))

    p = Paragraph(u'Observación:', negrita_custom(8))
    elements.append(p)
    elements.append(Spacer(1, 20 * mm))


    p = Paragraph(u'Director Técnico', negrita_custom(9,1))
    elements.append(p)


    doc.build(elements, onFirstPage = partial(self._header_footer, entrada = entrada),
      onLaterPages = partial(self._header_footer, entrada = entrada))

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
    subirmas = 7 * mm

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
    header.drawOn(canvas, doc.leftMargin + 16.8 * mm, doc.height + doc.topMargin - 69.6 * mm + subir + subirmas- 2*mm)

    header = Paragraph(venta.cliente.numero_documento, style)
    w, h = header.wrap(doc.width - 110 * mm, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin + 14.7 * mm, doc.height + doc.topMargin - 76.9 * mm + subir + subirmas- 2*mm)


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
    footer.drawOn(canvas, doc.leftMargin + 116.79 * mm, 28.2 * mm + subir + subirmas + 1*mm)

    footer = Paragraph(venta.ruc_transportista, style)
    w, h = footer.wrap(doc.width, doc.bottomMargin)
    footer.drawOn(canvas, doc.leftMargin + 116.79 * mm, 22.5 * mm + subir + subirmas + 1*mm)


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


