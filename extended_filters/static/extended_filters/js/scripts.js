if ($ === undefined) {
    $ = django.jQuery;
}

$(function () {
    $(document.body).on('click', '.date-range-filter-submit', function (e) {
        e.preventDefault();
        var $parent = $(this).parents('form');
        window.location = window.location.pathname + $parent.data('query-string') + '&' + $parent.serialize();
    });

    $(document.body).on('click', '.data-range-filter-reset', function (e) {
        e.preventDefault();
        window.location = window.location.pathname + $(this).parents('form').data('query-string');
    });

    $(document.body).on('click', '.submit-checkbox-filter', function (e) {
        e.preventDefault();
        var $parent = $(this).parent();
        var url = window.location.pathname + $parent.data('query-string');
        var checkboxes = $parent.find('input.checkbox-filter:checkbox:checked');
        if (checkboxes.length) {
            var fieldName = $parent.data('field');
            url += '&' + fieldName + '=';
            var values = $.map(checkboxes, function(n, i){
                  return n.value;
            }).join(',');
            window.location = url + values;
        } else {
            window.location = url;
        }
    });

    $(document.body).on('click', '.reset-checkbox-filter', function (e) {
        e.preventDefault();
        var $parent = $(this).parent();
        var checkboxes = $parent.find('input.checkbox-filter:checkbox:checked');
        checkboxes.each(function () {
            $(this).removeAttr('checked');
        });
        window.location = window.location.pathname + $parent.data('query-string');
    });
});