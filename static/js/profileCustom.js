jQuery(function ($) {
    $(document).ready(function (){
        $(".choose_existed_image").click(function(evnt){
            evnt.preventDefault();

            $(".choose_existed_image").find('img').attr("style", "border:1px solid #333333;");

            $(this).find("img").attr("style", "border: 3px solid #f2f2f2;");


            $("#save_and_close_existed_image").attr('href', $(this).attr('data_url'));
            $("#save_and_close_existed_image button").removeAttr('disabled');
        });
        $("#upload_image_button").click(function(evnt){
            evnt.preventDefault();
            $("#uploadImageModal #uploadimageform #file").click();
        });
        $("#uploadImageModal #uploadimageform #file").change(function(evnt){
            $("#uploadImageModal #uploadimageform").submit();
        });
        $(".userPic").mouseenter(function(){
            $("#transparent_button").show();
        });
        $(".userPic").mouseleave(function(){
            $("#transparent_button").hide();
        });
        $(".change_bg_form").submit(function(evnt){
            evnt.preventDefault();
            var path = window.location.pathname;
            if (path.indexOf('settings') > 0){
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
                        $("#header_background").removeAttr('data-nobg');
                        $("#header_background").removeAttr('style');
                        $("#header_background").attr('data-bg', 'true');
                        $("#header_background").css("background-image", "url("+data.resized_url+")");
                        $("#header_background").css('background-size', "100%");
                        $("#header_background").css('position','relative');
                        // $(".close").click();
                        $(".profCoverBackground").css( "z-index", "0" );
                        $("#save_background").text("Save position");
                        $("#save_background").css("display","block");
                        // $("#dropdown_bg").show();
                        // $("#first_bg_upload").hide();
                        window.location.href = window.location.pathname
                    }
                    if (data.status == 'error'){
                        alert(data.message);
                    }
                });
            }
        });
    });
});