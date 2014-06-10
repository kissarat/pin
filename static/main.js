$(document).ready(function() {
    var id;
    $("#remove_photo, #remove_photo1").click(function(e) {
        var result;
        result = window.confirm("Are you sure you want to remove this picture ?");
        if (!result) {
            e.preventDefault();
            e.event.stopPropagation();
            return false;
        }
        e.event.stopPropagation();
    });

    $("#switch1").mouseover(function() {
        return $("#menu1").show();
    });

    $("#switch1").mouseout(function() {
        return $("#menu1").hide();
    });

    $("#switch2").mouseover(function() {
        return $("#menu2").show();
    });

    $("#switch2").mouseout(function() {
        return $("#menu2").hide();
    });

    $("#switch3").mouseover(function() {
        return $("#menu3").show();
    });

    $("#switch3").mouseout(function() {
        return $("#menu3").hide();
    });

    $("#pin-not-added").click(function() {
        show_pins_date();
        $(".pin-not-added").each(function() {
            $(this).show();
        });
    });
    $("#pin-added").click(function() {
        $(".pin-not-added").each(function() {
            $(this).hide();
        });
        hide_pins_date();
    });
    id = $(".carousel2").find(".active").attr("photoid");
    $("#remove_photo").attr("href", "/photo/" + id + "/remove");
    $(".album_item").click(function() {
        id = $(this).attr("data-photoid");
        $("#remove_photo").attr("href", "/photo/" + id + "/remove");
    });
    $(".carousel1").carousel({
        interval: false
    });
    $(".carousel2").carousel({
        interval: false
    }).on("slid.bs.carousel", function(e) {
        var xx;
        xx = $(this);
        id = xx.find(".active").attr("photoid");
        $("#remove_photo").attr("href", "/photo/" + id + "/remove");
    });

    $( ".form_with_loading" ).submit(function( event ) {
        $("body").addClass("loading");
        // event.preventDefault();
  });

    $( ".link_with_loading" ).click(function() {
        $("body").addClass("loading");
        // event.preventDefault();
    });

    $("a.follow").click(function(event){
        event.preventDefault();
        $elem = $(this);
        $.get($elem.attr('href'), function(data){
            if (data == 'unfollowed'){
                status = "Follow"
            }
            else {
                status = "Unfollow"
            }
            $elem.text(status);
        });
    });

    $("li > #change_background").click(function(e){
        $(".profCoverBackground").css( "z-index", "0" );
        $("#save_background").text("Save position");
        $("#save_background").css("display","block");
        $("#instructionWrap").show();
        $("#transbox").css("cursor","move");
    });

    $("#save_background").click(function(e){
        var action = $("#save_background").text();
        $("#save_background").css("display","none");
        if (action == "Save position") {
            $(".profCoverBackground").css( "z-index", "2" );
        }
        $("#instructionWrap").hide();
        $("#transbox").css("cursor","default");
    });

    $("#dropdown_bg > ul").mouseleave(function(e){
        $("#dropdown_bg").removeClass("open");
    });

    $("#dropdown_bg").mouseenter(function(e){
        $("#dropdown_bg").css("display","block");
    });

    $(".profCoverBackground")
        .on( "mouseover", function() {
            $("#dropdown_bg").css({
              "display": "block"
            });
        })
        .on( "mouseleave", function() {
            $("#dropdown_bg").css({ "display": "none" }); 
        });
    });
    

function hide_pins_date() {
  $(".dateWrap").each(function() {
    if($('.dwContent .dwItem:not(.pin-not-added)', this).length == 0) {
      $(this).hide();
    }
  });
}

function show_pins_date() {
  $(".dateWrap").each(function() {
    $(this).show();
  });
}
