$(function ($) {
    $('.dal-admin-filter :input').change(function (e) {
      var val = $(this).val();
      var field_path = $(this).parents('.dal-admin-filter').data('field-path');
      if (val) {
        window.location = window.location.pathname + val;
      } else {
        var replace = field_path + '=' + new URL(location.href).searchParams.get(field_path);
        window.location = window.location.pathname + location.search.replace(replace, '');
      }
    })
});