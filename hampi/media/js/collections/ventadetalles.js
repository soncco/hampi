var intimpa = intimpa || {};

(function() {
  intimpa.VentaDetalles = Backbone.Collection.extend({
    model: intimpa.VentaDetalle,
    initialize: function() {}
  });

  intimpa.VentaDetallesCollection = new intimpa.VentaDetalles;
})();
