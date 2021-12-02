odoo.define("website_address_autocomplete_sepomex.form", function (require) {
    
    "use strict";
    
    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');
    $(document).ready(function() {
        publicWidget.registry.WebsiteSale.include({
            init: function () {
                this._super.apply(this, arguments);

                this._changeCartQuantity = _.debounce(this._changeCartQuantity.bind(this), 500);
                this._changeCountry = _.debounce(this._changeCountry.bind(this), 500);
                
                var selectCountries = $("select[name='country_id']");
    
                this.isWebsite = true;

                delete this.events['change .main_product:not(.in_cart) input.js_quantity'];
                delete this.events['change [data-attribute_exclusions]'];
            },
        })
        publicWidget.registry.AddressAutocomplete = publicWidget.Widget.extend({
            selector: ".zipcode_div",
            events: {
                "keyup input[name='zip']": "_getDataWithZipCode",
                "change input#changeInputs": "_changeInputs",
            },
            init: function() {
                setTimeout(() => {
                    this._getDataWithZipCode;    
                },
                5000 
                );
            },
            _getDataWithZipCode: function() {
                const ESTADO_ABREVIATURA = [
                    {'name': 'Aguascalientes', 'abv': 'AGU'},
                    {'name': 'Baja California', 'abv': 'BCN'},    
                    {'name': 'Baja California Sur', 'abv': 'BXS'},
                    {'name': 'Campeche', 'abv': 'CAM'},
                    {'name': 'Chihuahua', 'abv': 'CHH'},
                    {'name': 'Chiapas', 'abv': 'CHP'},
                    {'name': 'Coahuila de Zaragoza', 'abv': 'COA'},
                    {'name': 'Colima', 'abv': 'COL'},
                    {'name': 'Ciudad de México', 'abv': 'DIF'},
                    {'name': 'Durango', 'abv': 'DUR'},
                    {'name': 'Guerrero', 'abv': 'GRO'},
                    {'name': 'Guanajuato', 'abv': 'GUA'},
                    {'name': 'Guanajuato', 'abv': 'GUA'},
                    {'name': 'Hidalgo', 'abv': 'HID'},
                    {'name': 'Jalisco', 'abv': 'JAL'},
                    {'name': 'México', 'abv': 'MEX'},
                    {'name': 'Michoacán de Ocampo', 'abv': 'MIC'},
                    {'name': 'Morelos', 'abv': 'MOR'},
                    {'name': 'Nayarit', 'abv': 'NAY'},
                    {'name': 'Nuevo León', 'abv': 'NLE'},
                    {'name': 'Oaxaca', 'abv': 'OAX'},
                    {'name': 'Puebla', 'abv': 'PUE'},
                    {'name': 'Querétaro', 'abv': 'QUE'},
                    {'name': 'Quintana Roo', 'abv': 'ROO'},
                    {'name': 'San Luis Potosí', 'abv': 'SNP'},
                    {'name': 'Sinaloa', 'abv': 'SIN'},
                    {'name': 'Sonora', 'abv': 'SON'},
                    {'name': 'Tabasco', 'abv': 'TAB'},
                    {'name': 'Tamaulipas', 'abv': 'TAM'},
                    {'name': 'Tlaxcala', 'abv': 'TLA'},
                    {'name': 'Veracruz de Ignacio de la Llave', 'abv': 'VER'},
                    {'name': 'Yucatán', 'abv': 'YUC'},
                    {'name': 'Zacatecas' , 'abv':'ZAC'},
                ]

                if($('.div_error-zipcode').length) {
                    $('.div_error-zipcode').remove();
                }
                var zipcode = $("input[name='zip']").val();
                var selectCities = $("select[name='city_id']");
                var selectState = $("select[name='state_id']");
                if (zipcode.length == 5) {
                    $.ajax({
                        type: "GET",
                        url: "/sepomex",
                        data: "zipcode="+ zipcode,

                        success: function (response) {
                            var selectCountries = $("select[name='country_id']");
                            var data = JSON.parse(response);

                            if (data.error == undefined || data.code_error == 0) {
                                selectState.find("option:selected").removeAttr("selected");
                                if(data.estado_abreviatura != undefined){
                                    selectState.find(`option[id='${data.estado_abreviatura}']`).prop("selected", "true");
                                }
                                else{
                                    const abreviatura = ESTADO_ABREVIATURA.find( estado => estado.name === data.response.estado );
                                    
                                    selectState.find(`option[id=${abreviatura.abv}]`).prop("selected", "true");
                                }
                                $('input[name="l10n_mx_edi_colony"]').remove();
                                if(!$('select[name="l10n_mx_edi_colony"]').length) {
                                    $('<select name="l10n_mx_edi_colony" class="form-control"></select>').insertAfter('label[for="l10n_mx_edi_colony"]');
                                }
                                var data_muni =" ";
                                if (data.municipio != undefined)
                                    {
                                        data_muni = "municipio=" + data.municipio + "&state_id=" + selectState.val()
                                    }
                                else if(data.response.municipio != undefined)
                                    {
                                        data_muni = "municipio=" + data.response.municipio + "&state_id=" + selectState.val()
                                    }
                
                                $.ajax({
                                    type: "GET",
                                    url: '/get-cities',
                                    data: data_muni
                                    
                                }).then(function (city) {
                                    rpc.query({
                                        route: "/shop/state_infos/" + selectState.val(),
                                        params: {
                                            mode: "shipping",
                                        },
                                    }).then(function (data) {
                                        var city2 = JSON.parse(city);
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
                                                selectCities.find("option:selected").removeAttr("selected");
                                                selectCities.find(`option[value='${city2.id}']`).prop("selected", "true");
                                                selectCities.find(`option[value='${city2.id}']`).attr("selected", "selected");
                                                $("input[name='city']").attr('type','hidden');
                                                $("input[name='city']").val(city2.name);
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
                                });
                                $("#l10n_mx_edi_colony").find('option').remove();
                                
                                if (data.colonias != undefined)
                                    {
                                        $.each(data.colonias,function(key, value)
                                        {
                                            $("#l10n_mx_edi_colony").append(`<option value="${value.colonia}">${value.colonia}</option>`);
                                        });
                                    }
                                    
                                else if(data.response.asentamiento != undefined){
                                    $.each(data.response.asentamiento,function(key, value)
                                    {
                                        $("#l10n_mx_edi_colony").append(`<option value="${value}">${value}</option>`);
                                    });
                                }
                            }
                            else{
                                
                                if(!$('.div_error-zipcode').length) {
                                    $(`<div class="col-12 div_error-zipcode">
                                        <h5 class="error-zipcode text-danger font-weight-bold">No encontramos información del código postal, por favor rellena manualmente<h5>
                                    </row>`)
                                    .insertBefore('.div_zip');
                                }
                            }
                        },
                        error: function (error) {
                                
                                if(!$('.div_error-zipcode').length) {
                                    $(`<div class="col-12 div_error-zipcode">
                                        <h5 class="error-zipcode text-danger font-weight-bold">No encontramos información del código postal, por favor rellena manualmente<h5>
                                    </row>`)
                                    .insertBefore('.div_zip');
                                }
                                if(error.statusText === "timeout"){
                                    var selectCities = $("select[name='city_id']");
                                    var selectState = $("select[name='state_id']");
                                    selectCities.find('option').remove();
                                    selectCities.removeClass('d-block');
                                    selectCities.addClass('d-none');
                                    selectState.removeClass('pnone');
                                    selectState.addClass('pall')
                                    $("#changeInputs").prop("checked", true);
                                    $("input[name='city']").attr('type','text');
                                    $("input[name='city']").val('');
                                    $('.div_l10n_mx_edi_colony').append(`<input type="text" name="l10n_mx_edi_colony" class="form-control" t-att-value="'l10n_mx_edi_colony' in partner and partner['l10n_mx_edi_colony']" />`);
                                    $('select[name="l10n_mx_edi_colony"]').remove();
                                }
                            },
                        timeout: 10000
                        });
                        
                    }
                },
                _changeInputs: function(element) {
                    var selectCities = $("select[name='city_id']");
                    var selectState = $("select[name='state_id']");
                    if(element.target.checked) {
                        selectCities.find('option').remove();
                        selectCities.removeClass('d-block');
                        selectCities.addClass('d-none')
                        selectState.removeClass('pnone');
                        selectState.addClass('pall')
                        selectState.removeClass('pnone');
                        selectState.addClass('pall')
                        $("input[name='city']").removeClass('d-none');
                        $("input[name='city']").attr('type','text');
                        $("input[name='city']").val('');
                        if(!$('input[name="l10n_mx_edi_colony"]').length) {
                            $('.div_l10n_mx_edi_colony').append(`<input type="text" name="l10n_mx_edi_colony" class="form-control" t-att-value="'l10n_mx_edi_colony' in partner and partner['l10n_mx_edi_colony']" />`);
                        }
                        $('select[name="l10n_mx_edi_colony"]').remove();
                    }
                    else {
                        selectCities.removeClass('d-none');
                        selectCities.addClass('d-block');
                        selectCities.find('option').remove();
                        $("input[name='city']").attr('type','hidden');
                        $('input[name="l10n_mx_edi_colony"]').remove();
                        if(!$('select[name="l10n_mx_edi_colony"]').length) {
                            $('<select id="l10n_mx_edi_colony" name="l10n_mx_edi_colony" class="form-control"></select>').insertAfter('label[for="l10n_mx_edi_colony"]');
                        }
                        this._getDataWithZipCode();
                    }
                }
        });
    });
});