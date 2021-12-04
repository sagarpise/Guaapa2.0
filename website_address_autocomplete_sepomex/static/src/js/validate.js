odoo.define('website_form_address.validate', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;

    $( "form.checkout_autoformat" ).ready(function() {
        console.log( "ready! for short name" );
        var fullname = $("div.div_name > input").val();
        var short = String(fullname).split(",");
        if (short.length >= 3){
            $("div.div_name > input").val(short[0]);
            $("#lastname").val(short[1]);
            $("#lastname2").val(short[2]);
        }
    });

    $( "form.checkout_autoformat" ).submit(function( event ) {
        var nombre = $("div.div_name > input").val()
        var lastname = $("#lastname").val()
        var lastname2 = $("#lastname2").val()
        var fullname = nombre + "," + lastname + "," + lastname2
        $("div.div_name > input").val(fullname)
    });

});
