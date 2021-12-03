odoo.define('website_sale_refresh.navbar', function(require) {
    "use strict";

    var ajax = require('web.ajax');

    var ua = navigator.userAgent.toLowerCase();
    console.log(ua.indexOf('safari'))
    console.log(ua.indexOf('chrome'))
    console.log(ua.indexOf('firefox'))

    if (ua.indexOf('safari') != -1) {
        if (ua.indexOf('chrome') > -1) {
            console.log("Desde chrome");
            var back_navigation = performance.getEntriesByType("navigation");
            if (back_navigation[0].type === "back_forward") {
                ajax.jsonRpc('/navbar/shop/cart/update', 'call')
                    .then(function(data) {
                        console.log(data)
                        if ($('.my_cart_quantity')) {
                            $('.my_cart_quantity').html(data[0]);
                            $('.oe_currency_value:first').html(data[1]);
                            $('.products-cart').html(data[2]);
                            $('.footer-pay').html(data[3]);
                        }
                    })
            }
        } else {
            console.log("Desde safari");
            window.addEventListener("pageshow", function(event) {
                if (event.persisted) {
                    ajax.jsonRpc('/navbar/shop/cart/update', 'call')
                        .then(function(data) {
                            console.log(data)
                            if ($('.my_cart_quantity')) {
                                $('.my_cart_quantity').html(data[0]);
                                $('.oe_currency_value:first').html(data[1]);
                                $('.products-cart').html(data[2]);
                                $('.footer-pay').html(data[3]);
                            }
                        })
                }
            })
        }
    }
    if (ua.indexOf('firefox') > -1) {
        console.log("Desde firefox");
        var back_navigation = performance.getEntriesByType("navigation");
        if (back_navigation[0].type === "back_forward") {
            ajax.jsonRpc('/navbar/shop/cart/update', 'call')
                .then(function(data) {
                    console.log(data)
                    if ($('.my_cart_quantity')) {
                        $('.my_cart_quantity').html(data[0]);
                        $('.oe_currency_value:first').html(data[1]);
                        $('.products-cart').html(data[2]);
                        $('.footer-pay').html(data[3]);
                    }
                })
        }
    }
});
