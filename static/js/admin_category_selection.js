// Generated by CoffeeScript 1.4.0

jQuery(function() {
  var left, load_more_items, simplify_url, top;
  $.loading_items = false;
  $.current_page = 0;
  $.current_column = 1;
  $.pin_template = _.template($('#pin_template').html());
  load_more_items = function() {
    var url;
    if ($.loading_items) {
      return;
    }
    $.loading_items = true;
    url = '/admin/selection/pending_items?page=' + $.current_page;
    $.getJSON(url, function(data) {
      var pin, pin_html, _i, _len;
      for (_i = 0, _len = data.length; _i < _len; _i++) {
        pin = data[_i];
        if ($.current_column > 4) {
          $.current_column = 1;
        }
        pin['simplifiedurl'] = simplify_url(pin['link']);
        if (pin['tags'] !== null) {
          pin['taglist'] = pin['tags'];
        }
        pin_html = $.pin_template(pin);
        $('#column' + $.current_column).append(pin_html);
        $.current_column += 1;
      }
      $.loading_items = false;
    });
  };
  simplify_url = function(url) {
    var first_slash_position, simplified;
    simplified = url;
    if (simplified.indexOf('http:') === 0) {
      simplified = simplified.substring(6, simplified.length - 1);
    }
    if (simplified.indexOf('https:') === 0) {
      simplified = simplified.substring(7, simplified.length - 1);
    }
    if (simplified.indexOf('//') === 0) {
      simplified = simplified.substring(2, simplified.length - 1);
    }
    if (simplified.indexOf('/') === 0) {
      simplified = simplified.substring(1, simplified.length - 1);
    }
    first_slash_position = simplified.indexOf('/');
    if (first_slash_position > 0) {
      simplified = simplified.substring(0, first_slash_position);
    }
    return simplified;
  };
  $(document).on('click', 'div.category_pin', function(event) {
    var categories, categories_string, checkbox, data, pin, pin_id, url, _i, _len, _ref;
    categories = Array();
    _ref = $('input.category_check:checked');
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      checkbox = _ref[_i];
      categories.push(checkbox.value);
    }
    if (categories.length > 0) {
      categories_string = categories.join(',');
      console.log(categories_string);
      pin = $(this);
      pin_id = $(this).attr('pin_id');
      data = {
        pin_id: pin_id,
        categories: categories_string
      };
      url = '/admin/selection/add_to_categories';
      console.log(url);
      $.ajax({
        dataType: 'json',
        data: data,
        url: url,
        type: 'POST',
        success: function() {
          return pin.remove();
        }
      });
    }
  });
  $('input.category_check').on('change', function() {
    var parent_id;
    if (!this.checked) {
      return;
    }
    parent_id = $(this).attr('parent');
    if (parent_id === null) {
      return;
    }
    $('input.category_check').each(function() {
      var test_id;
      test_id = $(this).val();
      if (parent_id === test_id) {
        return $(this).prop('checked', true);
      }
    });
  });
  $(window).scroll(function() {
    var doc_height, height, sensitivity, top;
    top = $(window).scrollTop();
    height = $(window).innerHeight();
    doc_height = $(document).height();
    sensitivity = 10;
    if (top + height + sensitivity > doc_height) {
      $.current_page += 1;
      load_more_items();
    }
  });
  load_more_items();
  $('div.category_selection_list').show();
  top = $(window).height() - $('div.category_selection_list').height();
  left = ($(window).width() - $('div.category_selection_list').width()) / 2;
  $('div.category_selection_list').offset({
    'top': top,
    'left': left
  });
});
