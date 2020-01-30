import { isFormstageElement, buildElement } from 'src/lib/html.js'
// DAL needs the full version
import 'select2/dist/js/select2.full.js'
import 'select2/dist/css/select2.css'


// Initialize all dal elements (urlfunc is optional)
export function initDAL(urlfunc) {
    for (let element of document.querySelectorAll('[data-autocomplete-light-function=select2]')) {
        // If not inside a formstage
        if (!isFormstageElement(element)) {
            initDALWidget($(element), urlfunc)
        }
    }
}

// Build initial select2 element
function buildSelect2item(id, text, url) {
    let strong = document.createElement('strong');
    let id_text = buildElement('small', {}, `(id: ${id}) `)
    // Build link element
    let link = buildElement('a',
        {
            'class': 'ac_preview_link',
            'href': url,
            'target': 'preview',
            'title': 'Open in a new window',
        }
    )
    link.appendChild(buildElement('i', {'class': 'fa fa-external-link-square'}))
    // When clicking link open in small window
    link.addEventListener('click', () => {
        window.open(url, 'preview', 'height=600,width=595,resizeable=yes,scrollbars=yes')
    })
    // Add elements to strong
    strong.appendChild(document.createTextNode(text + ' '))
    strong.appendChild(id_text)
    strong.appendChild(link)
    return strong
}

// Initialize a single dal element (urlfunc is optional)
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
        // This is a blank entry, return nothing.
        if (item.id == "") {
            return item.text;
        }
        let url = item.element.getAttribute('data-item-url');
        // This is an item that was loaded with the page.
        if (item.id && !item.body) {
            return buildSelect2item(item.id, item.text, url)
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
        let url = ''
        if (urlfunc === undefined) {
            url = $(element).attr('data-autocomplete-light-url')
        } else {
            url = urlfunc(element)
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

    // Set the dropdown CSS class
    let dropdownCssClass = "aristotle-select2";
    if (element.attr('multiple')) {
        dropdownCssClass = 'aristotle-select2-multiple'
    }
    $(element).select2({
        tokenSeparators: element.attr('data-tags') ? [','] : null,
        debug: true,
        containerCssClass: ':all:',
        dropdownCssClass: dropdownCssClass,
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
