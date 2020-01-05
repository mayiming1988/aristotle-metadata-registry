import 'src/styles/aristotle.admin.less'
import 'src/styles/components/sidebar.less'

$( document ).ready( function() {
    $('div.suggest_name_wrapper button').click(function() {
        var fields = $(this).data('suggestFields').split(',');
        var sep = $(this).data('separator');
        if (!sep) {
            sep = "-"
        }
        var name = "";
        $.each(fields, function(i,field) {
            let input = $('#id_'+field);
            let field_name=input.val();
            if (input.parent().hasClass('autocomplete-light-widget')) {
                field_name=input.parent().find('.title').data('name');
                if (field_name){
                    field_name = field_name.trim();
                }
            }

            if (i==0) {
                name = field_name
            } else {
                name = name + sep + field_name;
            }
        })
        $(this).siblings('input').val(name);
        return false;
    });
});
