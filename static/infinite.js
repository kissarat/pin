$(document).ready(function() {
    var $box, $buffer, $button, addItem, appendPin, count, getMorePosts, $loading, numPins, offset;

    offset = 1;

    $loading = $('#small_loading_image');

    $box = $('#pin-box');

    $box.masonry({
        gutter: 16,
        transitionDuration: 0
    });
    
    var ww = window.innerWidth;
    if (ww<1000) $('body').addClass('small');
    else if (ww<1200) $('body').addClass('medium');
    else if (ww<1600) $('body').addClass('normal');
    else if (ww<1900) $('body').addClass('big');
    else $('body').addClass('large');

    //$button = $('#button-more');

    $buffer = $('#pin-buf');

    count = 0;

    $buffer.find('.pin').each(function() {
        return count++;
    });

    addItem = function(box, item) {
        return box.append(item)
            .masonry('appended', item);
//            .masonry('layout');
    };

    numPins = 0;

    $buffer.find('.pin').each(function() {
        var i = 0;
        var $pin = $(this);
        return imagesLoaded($pin.get(0), function() {
            $pin.remove();
            $pin.find('.count').text(++numPins);
            addItem($box, $pin);
            if ((++i) === count) {
                return $box.masonry('layout');
            }
        });
    });

    appendPin = function(jElem) {
        $buffer.append(jElem);
        return imagesLoaded(jElem.get(0), function() {
            var clone;
            clone = jElem.clone();
            jElem.remove();
            clone.find('.count').text(++numPins);
            return addItem($box, clone);
        });
    };

    getMorePosts = function() {
        offset++;
        $loading.css('display', 'block');
        return $.getJSON('', {
            offset: offset,
            ajax: 1
        }, function(data) {
            $loading.css('display', 'none');
            count = 0;
            if (data.length > 0) {
                //$button.prop('disabled', false);
                for (var i in data)
                    appendPin($(data[i]));
            } else {
                //$button[0].outerHTML = 'No more items to show!';
            }
        });
    };
/*
    $button.click(function() {
        $button.prop('disabled', true);
        if ('none' == $loading.css('display')) {
            return getMorePosts();
        }
    });
*/
    $(window).scroll(function() {
        if (((document.body.scrollHeight - innerHeight) - scrollY) < 240
                && 'none' == $loading.css('display'))
            getMorePosts();
    });

    //$button.prop('disabled', false);

    setInterval((function() {
        return $box.masonry('layout');
    }), 1000);

});
