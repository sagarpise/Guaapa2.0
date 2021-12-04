
 odoo.define('l10n_mx_website_sale.profile_hide_fields', function (require) {

    "use strict";

    function invoice_hide_fields (event) {
        if ($(this).find(":selected").val() == 'si'){
            $('#div_user_donde_trabaja').show();
            $('#div_user_cant_horas_work').show();
        }else{
            $('#div_user_donde_trabaja').hide();
            $('#div_user_cant_horas_work').hide();
        }
    }

    $("#user_trabaja").on("change", invoice_hide_fields);

});