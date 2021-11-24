$(document).ready(function(){
    var screensize = screen.width;
    var base_url =$("input[name=base_url]").val();
    var status =$("input[name=status]").val();
    if (status == 'verified' || status == 'already_verified')
    {
        var counter = 4 ;
        $("#loadImgWrap").show();
        $("#second_counter").text('Usted será redirigido en '+ 5 + ' secs.');
        var myInterval = setInterval(function () {
        if (counter > 0)
        {
            $("#second_counter").text('Usted será redirigido en '+ counter+ ' secs.');

        }
        else{
            if (screensize >= 700)
            {
                // window.location = base_url +'/web/login';
                location.assign(base_url)
            }
            else{
                location.assign(base_url)
            }
        }
        --counter;

    }, 1000);
    }
});
