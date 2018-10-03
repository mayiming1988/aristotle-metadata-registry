import { getCSRF } from './cookie.js'
// DAL needs the full version
import 'select2/dist/js/select2.full.js'
import 'select2/dist/css/select2.css'

export function initDAL() {
  $('[data-autocomplete-light-function=select2]').each(function() {
      var element = $(this);

      // Templating helper
      function template(text, is_html) {
          if (is_html) {
              var $result = $('<span>');
              $result.html(text);
              return $result;
          } else {
              return text;
          }
      }

      function result_template(item) {
          return template(item.text,
              element.attr('data-html') !== undefined || element.attr('data-result-html') !== undefined
          );
      }

      function selected_template(item) {
          if (item.selected_text !== undefined) {
              return template(item.selected_text,
                  element.attr('data-html') !== undefined || element.attr('data-selected-html') !== undefined
              );
          } else {
              return result_template(item);
          }
          return
      }

      var ajax = null;
      if ($(this).attr('data-autocomplete-light-url')) {
          ajax = {
              url: $(this).attr('data-autocomplete-light-url'),
              dataType: 'json',
              delay: 250,

              data: function (params) {
                  var data = {
                      q: params.term, // search term
                      page: params.page,
                      create: element.attr('data-autocomplete-light-create') && !element.attr('data-tags'),
                      // forward: null
                  };

                  return data;
              },
              processResults: function (data, page) {
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

      $(this).select2({
          tokenSeparators: element.attr('data-tags') ? [','] : null,
          debug: true,
          containerCssClass: ':all:',
          placeholder: element.attr('data-placeholder') || '',
          language: element.attr('data-autocomplete-light-language'),
          minimumInputLength: element.attr('data-minimum-input-length') || 0,
          allowClear: ! $(this).is('[required]'),
          templateResult: result_template,
          templateSelection: selected_template,
          ajax: ajax,
          tags: Boolean(element.attr('data-tags')),
      });

  })
}
