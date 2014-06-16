jQuery(function ($) {
    $(document).ready(function (){
        $(".album_details").click(function(evnt){
            var request_type = $(this).attr("data-id");
            var user_id = $(this).attr("data-userid");
            var data = {
                "user_id": user_id,
                "request_type": request_type
            }
            $.get("/ajax_album", data, function(data){
                $("#albums_list").html(data);

                $( ".link_with_loading" ).click(function() {
                    $("body").addClass("loading");
                });

                $("#photos_list").attr("onclick", "window.location.hash='#photos_list';window.location.reload(true);")
            });
        });
        $(".boardlink").click(function(event){

            event.preventDefault();
            var link = $(this).attr("href") + "?ajax=1";

            $.get(encodeURI(link), function(data){
                $("#list-box-wrapper").html(data);

                $(".link_with_loading").click(function() {
                    $("body").addClass("loading");
                });

                $("#list-box-wrapper-link").attr("onclick", "window.location.hash='#list-box-wrapper-link';window.location.reload(true);")
            });

        });

        $(".choose_existed_image").click(function(evnt){
            evnt.preventDefault();

            $(".choose_existed_image").find('img').attr("style", "border:1px solid #333333;");

            $(this).find("img").attr("style", "border: 3px solid #f2f2f2;");


            $("#save_and_close_existed_image").attr('href', $(this).attr('data_url'));
            $("#save_and_close_existed_image button").removeAttr('disabled');
        });
        $(".choose_existed_bg").click(function(evnt){
            evnt.preventDefault();

            $(".choose_existed_bg").find('img').attr("style", "border:1px solid #333333;");

            $(this).find("img").attr("style", "border: 3px solid #f2f2f2;");


            $("#save_and_close_existed_bg").attr('href', $(this).attr('data_url'));
            $("#save_and_close_existed_bg button").removeAttr('disabled');
        });
        $("#upload_image_button").click(function(evnt){
            evnt.preventDefault();
            $("#uploadImageModal #uploadimageform #file").click();
        });
        $("#upload_bgimage_button").click(function(evnt){
            console.log("Clicked")
            evnt.preventDefault();
            $("#uploadBackgroundImageModal #uploadimageform #file").click();
        });

        $("#uploadBackgroundImageModal #uploadimageform #file").change(function(evnt){
            $("#uploadBackgroundImageModal #uploadimageform").submit();
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

        /*$('.enlarge').click(function() {
            $('#enlarged-img').attr('src', $(this).attr('data-src'));
            $('#enlargeImage').modal('show');

            return false;
        });*/
    });
});
