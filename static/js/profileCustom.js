jQuery(function ($) {
    $(document).ready(function (){
        $(".change_bg_form").submit(function(evnt){
            evnt.preventDefault();
            var path = window.location.pathname;
            if (path.indexOf('settings')){
                // If user is on 'settings' page
                $(this).ajaxSubmit(function(data){
                    if (data.status == "ok"){
                        if($('#user_background_settings').length) {
                            $('#user_background_settings').attr('src', data.resized_url);
                        }
                        if($('#user_background_settings_span').length) {
                            var img = "<img id='user_background_settings' class='avatar' src='"+data.resized_url+"' style='width:44px;' />";
                            $(img).insertAfter('#user_background_settings_span');
                            $('#user_background_settings_span').remove();
                        }
                        $("body").removeClass("loading");
                        $(".close").click();
                    }
                    if (data.status == 'error'){
                        alert(data.message);
                    }
                });
            }
            else{
                // If user on his profile page
                $(this).ajaxSubmit(function(data){
                    if (data.status == "ok"){
                        $("#header_background").css("background-image", "url("+data.resized_url+")");
                        $(".close").click();
                    }
                    if (data.status == 'error'){
                        alert(data.message);
                    }
                });
            }
        });
    });
});