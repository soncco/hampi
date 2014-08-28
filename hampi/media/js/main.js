var intimpa = intimpa || {};

(function($) {
  $('.datepicker').datepicker({
    changeMonth: true,
    changeYear: true,
    dateFormat: 'yy-mm-dd'
  });

  intimpa.betterAlert = function() {}
  intimpa.betterAlert.warning = function(message) {
    html = '<div class="alert alert-warning animated bounceIn">'
              + '<a class="close" data-dismiss="alert" href="#" aria-hidden="true">&times;</a>'
              + '<p>' + message + '</p>'
            + '</div>';
    $('#messages').html(html);
  }

})(jQuery)
