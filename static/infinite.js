(function() {
    var offset = 1;
    var numPins = 0;
    var loading = false;
    var $box = $('#pin-box');
    var $button = $('#button-more');
    var $buffer = $('#pin-buf');
    var count = $buffer.find('.pin').length;

    $box.masonry({
        gutter: 20,
        transitionDuration: 0
    });

    function onImagesLoaded() {
        var $clone = this.clone();
        this.remove();
        $clone
            .find('.count')
            .text(++numPins);
        $box
            .append(item)
            .masonry('appended', item);
    }

    $buffer.find('.pin').each(function() {
        var $pin = $(this);
        imagesLoaded($pin, onImagesLoaded.bind($pin));
    });

    function getMorePosts() {
        offset++;
        loading = true;
        $.getJSON('', {
            offset: offset,
            ajax: 1 //WTF?
        }, function(data) {
            loading = false;
            count = 0;
            if (data.length > 0) {
                $button.prop('disabled', false);
                for (var i in data) {
                    var $pin = $(data[i]);
                    $buffer.append($pin);
                    imagesLoaded($pin, onImagesLoaded.bind($pin));
                }

            } else
                $button[0].outerHTML = 'No more items to show!';

        });
    }

    $button.click(function() {
        $button.prop('disabled', true);
        if (!loading)
            getMorePosts();
    });

    $button.prop('disabled', false);

    var requestAnimationFrame = window.requestAnimationFrame || function(paint) {
       setInterval(paint, 1000/25);
    };

    requestAnimationFrame(function() {
        $box.masonry('layout');
    });

}).call(this);
