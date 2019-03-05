// DAL needs the full version
import 'select2/dist/js/select2.full.js'
import 'select2/dist/css/select2.css'


export function initDAL(urlfunc) {
    $('[data-autocomplete-light-function=select2]').each(function() {
        var element = $(this);
        if (element.closest(".formstage").length == 0) {
            initDALWidget(element, urlfunc)
        }
    })
}

export function initDALWidget(element, urlfunc) {
    // Templating result
    function template_result(item) {
        if (!item.body) {
            return item.text;
        }
        if (element.attr('data-html') !== undefined) {
            var $result = $('<span>');
            $result.html(item.body);
            /* inserted for Aristotle */
                $result.on('mouseup', '.ac_preview_link', function(e) {
                    e.stopPropagation();
                    //return false;
                });
            /* end insert */
                return $result;
        } else {
            return item.body;
        }
    }

    // Templating selected item
    function template_selection(item) {
        if (!item.body) {
            return item.text;
        }
        if (element.attr('data-html') !== undefined) {
            var $result = $('<span>');
            $result.html(item.body);
            /* inserted for Aristotle */
                /* end insert */
                var title = $result.find(".title")
            if (title.length > 0) {
                var $title = $(title[0]);
                $title.on('mouseup', '.ac_preview_link', function(e) {
                    e.stopPropagation();
                    //return false;
                });

                return $title
            } else {
                return item.title;
            }
        } else {
            return item.title;
        }
    }

    let ajax = null;
    if ($(element).attr('data-autocomplete-light-url')) {
        let url = urlfunc
        if (urlfunc === undefined) {
            url = $(element).attr('data-autocomplete-light-url')
        }
        ajax = {
            url: url,
            dataType: 'json',
            delay: 250,

            data: function (params) {
                let data = {
                    q: params.term, // search term
                    page: params.page,
                    create: element.attr('data-autocomplete-light-create') && !element.attr('data-tags'),
                };
                return data;
            },
            processResults: function (data) {
                if (element.attr('data-tags')) {
                    $.each(data.results, function(index, value) {
                        value.id = value.text;
                    });
                }

                return data;
            },
            cache: true
        };
    }

    $(element).select2({
        tokenSeparators: element.attr('data-tags') ? [','] : null,
        debug: true,
        containerCssClass: ':all:',
        placeholder: element.attr('data-placeholder') || '',
        language: element.attr('data-autocomplete-light-language'),
        minimumInputLength: element.attr('data-minimum-input-length') || 0,
        allowClear: ! $(element).is('[required]'),
        templateResult: template_result,
        templateSelection: template_selection,
        ajax: ajax,
        tags: Boolean(element.attr('data-tags')),
    });
}
