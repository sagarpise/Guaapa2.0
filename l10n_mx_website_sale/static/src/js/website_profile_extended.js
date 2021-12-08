
 odoo.define('l10n_mx_website_sale.profile_hide_fields', function (require) {

    "use strict";
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
    $('input').keydown( function() {    
        $(":focus").removeClass("is-invalid-guaapa");
    });
});