odoo.define("l10n_mx_website_sale.portal", function (require) {
    "use strict";

    require("web.dom_ready");
    require("portal.portal");
    require("l10n_mx_website_sale.website_sale");

    var sAnimations = require("website.content.snippets.animation");

    sAnimations.registry.WebsitePortalCity = sAnimations.Class.extend({
        selector: ".o_portal_details",
        read_events: {
            'change select[name="state_id"]': "_onChangeState",
            'change select[name="city_id"]': "_onChangeCity",
        },

        init: function () {
            this._super.apply(this, arguments);
            this._changeState = _.debounce(this._changeState.bind(this), 500);
            this.isWebsite = true;
        },

        start: function () {
            var def = this._super.apply(this, arguments);
            this.$('select[name="state_id"]').change();
            return def;
        },

        _onChangeCity: function () {
            if (!$("select[name='city_id']").val()) {
                return;
            }
            var selectCity = $('select[name="city_id"] option:selected');
            var zipcode = selectCity.attr("data-code");

            //$("input[name='zipcode']").val(zipcode);
            $("input[name='city']").val(selectCity.text());
        },

        _onChangeState: function () {
            this._changeState();
        },

        _changeState: function () {
            var state_id = $("select[name='state_id']");
            if (!state_id.val()) {
                return;
            }
            this._rpc({
                route: "/shop/state_infos/" + state_id.val(),
                params: {
                    mode: "shipping",
                },
            }).then(function (data) {
                // populate states and display
                var selectCities = $("select[name='city_id']");
                var selected = selectCities.data("value");
                // Dont reload state at first loading (done in qweb)
                if (selectCities.data("init") === 0 || selectCities.find("option").length === 1) {
                    if (data.cities.length) {
                        $("input[name='city']").parent("div").hide();
                        selectCities.html("");
                        _.each(data.cities, function (x) {
                            var opt = $("<option>")
                                .text(x[1])
                                .attr("value", x[0])
                                .attr("data-code", x[2])
                                .attr("selected", x[0] === selected);
                            selectCities.append(opt);
                        });
                        selectCities.parent("div").show();
                    } else {
                        selectCities.val("").parent("div").hide();
                        $("input[name='city']").parent("div").show();
                    }
                    selectCities.data("init", 0);
                } else {
                    selectCities.data("init", 0);
                }
            });
        },
    });
});

odoo.define("l10n_mx_website_sale.website_sale", function (require) {
    "use strict";

    require("website_sale.website_sale");
    var sAnimations = require("website.content.snippets.animation");
    var publicWidget = require('web.public.widget');
    
    sAnimations.registry.WebsiteSaleCity = sAnimations.Class.extend({
        selector: ".oe_website_sale",
        read_events: {
            'change select[name="country_id"]': "_onChangeCountry",
            'change select[name="state_id"]': "_onChangeState",
            'change select[name="city_id"]': "_onChangeCity",
        },
        
        init: function () {
            this._super.apply(this, arguments);
            this._changeState = _.debounce(this._changeState.bind(this), 600);
            this.isWebsite = true;
            this._onChangeState();
            var error_city = $('select[name="city_id"]');
            if(error_city.hasClass( "error_city" )){
                error_city.removeClass("d-block");
                if(!error_city.hasClass('d-none')){
                    error_city.addClass('d-none');
                }
            }
        },

        start: function () {
            var def = this._super.apply(this, arguments);
            return def;
        },

        _onChangeCountry: function () {
            var selectCities = $("select[name='city_id']");
            selectCities.parent("div").hide();
            $("input[name='city']").parent("div").show();
        },

        _onChangeCity: function () {
            if (!$("select[name='city_id']").val()) {
                return;
            }
            var selectCity = $('select[name="city_id"] option:selected');
            var zipcode = selectCity.attr("data-code");

            $("input[name='zip']").val(zipcode);
            $("input[name='city']").val(selectCity.text());
        },

        _onChangeState: function () {
            this._changeState();
            this._onChangeCity();
        },

        _changeState: function () {
            var selectCities = $("select[name='city_id']");
            var selectState = $("select[name='state_id']");

            if (!selectState.val()) {
                return;
            }
            this._rpc({
                route: "/shop/state_infos/" + selectState.val(),
                params: {
                    mode: "shipping",
                },
            }).then(function (data) {
                var selected = selectCities.data("value");
                if (selectCities.data("init") === 0 || selectCities.find("option").length === 1) {
                    if (data.cities.length) {
                        selectCities.html("");
                        _.each(data.cities, function (x) {
                            var opt = $("<option>")
                                .text(x[1])
                                .attr("value", x[0])
                                .attr("data-code", x[2])
                                .attr("selected", x[0] === selected);
                            selectCities.append(opt);
                        });
                        $("input[name='city']").attr('type','hidden');
                        selectCities.addClass('d-block');
                        selectCities.removeClass('d-none');
                    } else {
                        selectCities.find('option').remove();
                        selectCities.removeClass('d-block');
                        selectCities.addClass('d-none')
                        $("input[name='city']").attr('type','text');
                        $("input[name='city']").val('');
                    }
                    selectCities.data("init", 0);
                } else {
                    selectCities.data("init", 0);
                }
            });
        },
    });
    
    publicWidget.registry.WebsiteSale.include({
        _changeCountry: function () {
            if (!$("#country_id").val()) {
                return;
            }
            this._rpc({
                route: "/shop/country_infos/" + $("#country_id").val(),
                params: {
                    mode: $("#country_id").attr('mode'),
                },
            }).then(function (data) {
                // placeholder 
                //alert(JSON.stringify(data))
                $("input[name='phone']").attr('placeholder', data.phone_code !== 0 ? '+'+ data.phone_code : '');
    
                // populate states and display
                var selectStates = $("select[name='state_id']");
                // dont reload state at first loading (done in qweb)
                //alert(selectStates.data('init'))
                
                if (selectStates.data('init')===1) {
                    if (data.states.length || data.state_required) {
                        selectStates.html('');
                        _.each(data.states, function (x) {
                            var opt = $('<option>').text(x[1])
                                .attr('value', x[0])
                                .attr('data-code', x[2]);
                            selectStates.append(opt);
                        });
                        selectStates.parent('div').show();
                    } else {
                        selectStates.val('').parent('div').hide();
                    }
                    selectStates.data('init', 0);
                } else {
                    selectStates.data('init', 0);
                }
    
                // manage fields order / visibility
                if (data.fields) {
                    var all_fields = ["street", "zip", "city", "country_name"]; // "state_code"];
                    _.each(all_fields, function (field) {
                        $(".checkout_autoformat .div_" + field.split('_')[0]).toggle($.inArray(field, data.fields)>=0);
                    });
                }
    
                if ($("label[for='zip']").length) {
                    $("label[for='zip']").toggleClass('label-optional', !data.zip_required);
                    $("label[for='zip']").get(0).toggleAttribute('required', !!data.zip_required);
                }
                if ($("label[for='zip']").length) {
                    $("label[for='state_id']").toggleClass('label-optional', !data.state_required);
                    $("label[for='state_id']").get(0).toggleAttribute('required', !!data.state_required);
                }
            });
        }
    });
});