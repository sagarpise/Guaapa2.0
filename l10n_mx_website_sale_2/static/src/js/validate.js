odoo.define('l10n_mx_website_sale_2.validate', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var _t = core._t;

      function invoice_hide_fields (event) {
        if (this.checked){
            $('#div_vat').show();
            $('#div_company_name').show();
        }else{
            $('#div_vat').hide();
            $('#div_company_name').hide();
        }
    }

    $("#ref-code-signup-checkbox").on("change", invoice_hide_fields);

    // $(document).ready(function () {
    //     $('#ref-code-signup-checkbox').on('change', function () {
    //         if (this.checked) {
    //             $('#div_company_name').css('display', '');
    //             $('#company_name').attr('required', 'True');
    //         } else {
    //             $('#div_company_name').css('display', 'none');
    //             $('#company_name').removeAttr('required');
    //             $('#company_name').val('');
    //
    //         }
    //
    //     });
    //
    // });
});
