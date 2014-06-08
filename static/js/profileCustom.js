jQuery(function ($) {
    $(document).ready(function (){
        $(".change_bg_form").submit(function(evnt){
            evnt.preventDefault();
            $(this).ajaxSubmit(function(data){
                if (data.status == "ok"){
                    $("#header_background").css("background-image", "url("+data.resized_url+")");
                    $(".close").click();
                }
                if (data.status == 'error'){
                    alert(data.message);
                }
            });
        });
    });
});