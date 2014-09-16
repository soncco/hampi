var intimpa = intimpa || {};

(function() {
  intimpa.CotizacionDetalles = Backbone.Collection.extend({
    model: intimpa.CotizacionDetalle,
    initialize: function() {}
  });

  intimpa.CotizacionDetallesCollection = new intimpa.CotizacionDetalles;
})();
