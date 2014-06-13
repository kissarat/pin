$("#myTab").ready(function() {
    $('.profile_tabs_link').click(function(e) {
      location.hash = this.id;
      e.preventDefault();
    });

    var hash = window.location.hash;
    if(hash) {
        //$(hash).click();

        $("#myTab li.active").removeClass('active');
        $(hash).parent().addClass('active');

        $('.tab-pane.active').removeClass('active').removeClass('in');
        $($(hash).attr('href')).addClass('active').addClass('in');
    }
});
