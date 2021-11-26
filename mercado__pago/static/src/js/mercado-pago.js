odoo.define('module.MP', function(require) 
{
    "use strict";
    var rpc = require('web.rpc');

    $(document).ready(function() 
    {

        var url_string = window.location.href;
        var url = new URL(url_string);
        var state = url.searchParams.get("state");

        if (state == "quoted") {
            swal({
                title: "Cotización",
                text: "Gracias, recibimos la solicitud de su pedido, pero el pago esta pendiente. \n Puede ver mas información en mi cuenta > Cotizaciónes",
                type: "success",
                showCancelButton: true,
                cancelButtonText: "OK",
                closeOnCancel: true
            });
        }

        if (state == "done") {
            swal({
                title: "Orden de venta",
                text: "Gracias, el pedido esta hecho, verificamos que su pago se haya acreditado en nuestra cuenta para confirmar la orden de venta. \n Puede ver mas información en mi cuenta > Ordenes de venta",
                type: "success",
                showCancelButton: true,
                cancelButtonText: "OK",
                closeOnCancel: true
            });
        }

        if (state == "fail") {
            swal({
                title: "Orden de venta",
                text: "Gracias, la solicitud del pedido esta hecha pero el pago falló. Intenta de nuevo!",
                type: "warning",
                showCancelButton: true,
                cancelButtonText: "OK",
                closeOnCancel: true
            });
        }
        
        
        var default_button = $("form.o_payment_form").find("button#o_payment_form_pay");

        if ($("#payment_method").length > 0) {
            $("#o_payment_form_pay").after(function() {
                initmercadopagoAcquirer();                
            });
        }
        
        $("button#o_payment_form_pay").on("click",function()
        {
            event.preventDefault();
            var data_provider = $("input[name='pm_id']:checked").attr("data-provider");
            if(data_provider=="mercadopago")
            {
                var action = $("#mercadopago-form").attr("action");
                window.location.href = action
            }     
            else{
                if(data_provider!="payu")
                    $("form.o_payment_form").submit();
            }       
        });
    });

    function initmercadopagoAcquirer()
    {
        var data = { "params": {  } }
            $.ajax({
                type: "POST",
                url: '/mercadopago/get_mercadopago_acquirer',
                data: JSON.stringify(data),
                dataType: 'json',
                contentType: "application/json",
                async: false,
                success: function(response) {       

                    var acquirer = response.result.acquirer;
                    var bill_form = response.result.bill_form;

                    if(String(acquirer.state)=="enabled" || String(acquirer.state)=="test")
                    {

                       $("#o_payment_form_pay").after(function() 
                       {
                           // return "<button id='billmercadopago' class='btn btn-primary'>Pagar ahora <i class='fa fa-chevron-right'></i></button>";                
                       });

                       if(acquirer.mp_service_mode=="basic")
                       {
                            $(".oe_cart").append(bill_form);
                            createPreference(acquirer);
                       }
                       else // custom one
                       {                            
                            $( String("#o_payment_form_acq_") + String(acquirer.id) ).before(bill_form);
                            initCustomForm(acquirer);
                       }

                    }                    
                }
            });
    }

    function initCustomForm(acquirer)
    {
        var mercado_pago = new MercadoPago(String(acquirer.mp_public_key));
        initCustomCheckout(mercado_pago);

        $('input[name="pm_id"]').on('click', function(){
            var provider = $('input[name="pm_id"]:checked').attr("data-provider");
            if(provider == "mercadopago")
            {
                $(".form-mercadopago-custom").fadeIn();
            }
            else
            {
                $(".form-mercadopago-custom").fadeOut();
            }
        });
    }

    function initCustomCheckout(mercado_pago)
    {
        var partner_id = $(".o_payment_form").attr("data-partner-id");
        var acquirer_id = $('input[name="pm_id"]:checked').attr("data-acquirer-id");
        var data = { "params": { partner_id: partner_id, acquirer_id: acquirer_id } }
        $.ajax({
            type: "POST",
            url: '/mercadopago/get_sale_order',
            data: JSON.stringify(data),
            dataType: 'json',
            contentType: "application/json",
            async: false,
            success: function(response) 
            {
                try
                    {
                        var json_preference = response.result.json_preference;
                        console.log('initCustomCheckout');
                        console.log(json_preference);

                        $("input[name='cardholderName']").val(json_preference.payer.name);
                        var total_amount = getTotalAmount(json_preference.items);

                        console.log(total_amount);

                        var cardForm = mercado_pago.cardForm({
                            amount: String(total_amount),
                            autoMount: true,
                            form: {
                            id: "form-checkout",
                            cardholderName: {
                                id: "form-checkout__cardholderName",
                                placeholder: "Titular",
                            },
                            cardholderEmail: {
                                id: "form-checkout__cardholderEmail",
                                placeholder: "Correo electrónico",
                            },
                            cardNumber: {
                                id: "form-checkout__cardNumber",
                                placeholder: "Número de la tarjeta",
                            },
                            cardExpirationMonth: {
                                id: "form-checkout__cardExpirationMonth",
                                placeholder: "Mes",
                            },
                            cardExpirationYear: {
                                id: "form-checkout__cardExpirationYear",
                                placeholder: "Año",
                            },
                            securityCode: {
                                id: "form-checkout__securityCode",
                                placeholder: "CVV",
                            },
                            installments: {
                                id: "form-checkout__installments",
                                placeholder: "Cuotas",
                            },
                            identificationType: {
                                id: "form-checkout__identificationType",
                                placeholder: "Tipo de documento",
                            },
                            identificationNumber: {
                                id: "form-checkout__identificationNumber",
                                placeholder: "Número de documento",
                            },
                            issuer: {
                                id: "form-checkout__issuer",
                                placeholder: "Banco emisor",
                            },
                            },
                            callbacks: {
                            onFormMounted: error => {
                                if (error) return console.warn("Form Mounted handling error: ", error);
                                console.log("Form mounted");
                            },
                            onSubmit: event => {
                                event.preventDefault();
                        
                                const {
                                paymentMethodId: payment_method_id,
                                issuerId: issuer_id,
                                cardholderEmail: email,
                                amount,
                                token,
                                installments,
                                identificationNumber,
                                identificationType,
                                } = cardForm.getCardFormData();
                        
                                fetch("/process_payment", {
                                method: "POST",
                                headers: {
                                    "Content-Type": "application/json",
                                },
                                body: JSON.stringify({
                                    token,
                                    issuer_id,
                                    payment_method_id,
                                    transaction_amount: Number(amount),
                                    installments: Number(installments),
                                    description: "Descripción del producto",
                                    payer: {
                                    email,
                                    identification: {
                                        type: identificationType,
                                        number: identificationNumber,
                                    },
                                    },
                                }),
                                });
                            },
                            onFetching: (resource) => {
                                console.log("Fetching resource: ", resource);
                        
                                // Animate progress bar
                                const progressBar = document.querySelector(".progress-bar");
                                progressBar.removeAttribute("value");
                        
                                return () => {
                                progressBar.setAttribute("value", "0");
                                };
                            },
                            },
                        });
                    }
                catch(error)
                    {console.log(error)}                                              
            }
        });        
    }
    
    function createPreference(acquirer)
    {
        
        var partner_id = $(".o_payment_form").attr("data-partner-id");
        var acquirer_id = $('input[name="pm_id"]:checked').attr("data-acquirer-id");
        var data = { "params": { partner_id: partner_id, acquirer_id: acquirer_id } }
        $.ajax({
            type: "POST",
            url: '/mercadopago/get_sale_order',
            data: JSON.stringify(data),
            dataType: 'json',
            contentType: "application/json",
            async: false,
            success: function(response) 
            {
                try
                    {
                        var json_preference = JSON.parse(response.result.json_preference);
                        var preference = json_preference.response
                        var environment = response.result.environment;
                        var mercadopago_form = $('#mercadopago-form');

                        if(String(acquirer.state)=="test")
                        {                    
                            mercadopago_form.attr("action",preference.sandbox_init_point);
                        }
                        else
                        {             
                            mercadopago_form.attr("action",preference.init_point);
                        }       
                    }
                catch(error)
                    {console.log(error)}                                              
            }
        });
    }

    function getTotalAmount(items)
    {
        var total_amount = 0;
        if(items)
        {
            items.forEach(function(item) {
                console.log(item);
                total_amount = total_amount + ( parseFloat(item.unit_price) * parseFloat(item.quantity) );
              });
        }
        return total_amount;
    }
});