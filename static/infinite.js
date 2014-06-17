(function() {
  var $box, $buffer, $button, addItem, appendPin, count, getMorePosts, loading, numPins, offset;

  offset = 1;

  loading = false;

  $box = $('#pin-box');

  $box.masonry({
    gutter: 20,
    transitionDuration: 0
  });

  $button = $('#button-more');

  $buffer = $('#pin-buf');

  count = 0;

  $buffer.find('.pin').each(function() {
    return count++;
  });

  addItem = function(box, item) {
    return box.append(item).masonry('appended', item).masonry('layout');
  };

  numPins = 0;

  $buffer.find('.pin').each(function() {
    var $pin, i;
    $pin = $(this);
    i = 0;
    return imagesLoaded($pin, function() {
      var $clone;
      $clone = $pin.clone();
      $pin.remove();
      $clone.find('.count').text(++numPins);
      addItem($box, $clone);
      if ((++i) === count) {
        return $box.masonry('layout');
      }
    });
  });

  appendPin = function(jElem) {
    $buffer.append(jElem);
    return imagesLoaded(jElem, function() {
      var clone;
      clone = jElem.clone();
      jElem.remove();
      clone.find('.count').text(++numPins);
      return addItem($box, clone);
    });
  };

  getMorePosts = function() {
    offset++;
    loading = true;
    return $.getJSON('', {
      offset: offset,
      ajax: 1
    }, function(data) {
      var pin, _i, _len, _results;
      loading = false;
      count = 0;
      if (data.length > 0) {
        $button.prop('disabled', false);
        _results = [];
        for (_i = 0, _len = data.length; _i < _len; _i++) {
          pin = data[_i];
          _results.push(appendPin($(pin)));
        }
        return _results;
      } else {
        return $button[0].outerHTML = 'No more items to show!';
      }
    });
  };

  $button.click(function() {
    $button.prop('disabled', true);
    if (!loading) {
      return getMorePosts();
    }
  });

  $button.prop('disabled', false);

  setInterval((function() {
    return $box.masonry('layout');
  }), 100);

}).call(this);