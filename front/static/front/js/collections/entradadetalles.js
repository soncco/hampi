var intimpa = intimpa || {};

(function() {
  intimpa.EntradaDetalles = Backbone.Collection.extend({
    model: intimpa.EntradaDetalle,
    initialize: function() {}
  });

  intimpa.EntradaDetallesCollection = new intimpa.EntradaDetalles;
})();
