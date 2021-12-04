odoo.define("website_address_autocomplete_sepomex.website_sale", function (require) {
    "use strict";

    require("l10n_mx_website_sale.website_sale");
    var sAnimations = require("website.content.snippets.animation");

    sAnimations.registry.WebsiteSaleCity.include({
        _onChangeCity: function () {        
            if (!$("select[name='city_id']").val()) {
                return;
            }
            
            var selectCity = $('select[name="city_id"] option:selected');
            var zipcode = selectCity.attr("data-code");

            //$("input[name='zip']").val(zipcode);
            $("input[name='city']").val(selectCity.text());
        },
    });
});