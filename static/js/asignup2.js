// Generated by CoffeeScript 1.4.0
var add_pin_to_user, click_to_add_pin, hide_buttons, pin_count, remove_pin_from_user, show_button_add, show_button_remove, show_cover;

pin_count = 0;

$.column_control = 1;

$.add_pin_to_page = function(pin) {
  if ($.column_control > 3) {
    $.column_control = 1;
  }
  $('.column' + $.column_control).append('<div class="shadowbox">' + '<div class="pin-image" pinid="' + pin['id'] + '">' + '<img class="img-responsive" src="' + pin['image_202_url'] + '"/>' + '</div></div>');
  $.column_control += 1;
};

$('body').on('mouseleave', '.pin-add-button', function() {
  console.log('remove');
  $(this).remove();
});

$('body').on('click', '.select_pins', function(event) {
  event.stopPropagation();
  return click_to_add_pin($(this));
});

$('body').on('click', '.pin-add-button', function() {
  return click_to_add_pin($(this));
});

click_to_add_pin = function(elem) {
  var pin_id;
  pin_id = elem.attr('pinid');
  console.log(pin_id);
  add_pin_to_user(pin_id);
  show_cover(pin_id);
};

show_button_add = function(original_div, pin_id) {
  var cover_div, selection_button;
  $('body').append('<div class="pin-add-button" pinid="' + pin_id + '">' + '<button class="select_pins" style="margin-bottom: 10px;" pinid="' + pin_id + '">Get it</button>' + '</div>');
  cover_div = $('.pin-add-button[pinid="' + pin_id + '"]');
  cover_div.offset(original_div.offset());
  cover_div.width(original_div.width() + 3);
  cover_div.height(original_div.height() + 3);
  cover_div.css("z-index", pin_id);
  selection_button = $('.select_pins[pinid="' + pin_id + '"]');
  selection_button.css('margin-top', (original_div.height() / 2) - (selection_button.height() / 2));
  cover_div.css("visibility", "visible");
  console.log('show');
};

show_button_remove = function(original_div, pin_id) {};

hide_buttons = function(pin_id) {
  var cover_div;
  console.log('remove');
  cover_div = $('.pin-add-button[pinid="' + pin_id + '"]');
  return cover_div.css("visibility", "hidden");
};

$('body').on('mouseenter', ".pin-image", function() {
  var image, pin_id;
  console.log('hover');
  image = $(this).children('img:first');
  pin_id = $(this).attr('pinid');
  if ($(this).hasClass("selected")) {
    show_button_remove($(this), pin_id);
  } else {
    show_button_add($(this), pin_id);
  }
});

$('body').on('click', '.cover', function() {
  var original_div, pin_id;
  pin_id = $(this).attr('pinid');
  original_div = $(this);
  remove_pin_from_user(pin_id);
  return original_div.remove();
});

show_cover = function(pin_id) {
  var cover_div, original_div;
  original_div = $('.pin-image[pinid="' + pin_id + '"]');
  $('body').append('<div class="cover" pinid="' + pin_id + '"><div class="txtselected">selected</div></div>');
  cover_div = $('div.cover[pinid="' + pin_id + '"]');
  cover_div.offset(original_div.offset());
  cover_div.width(original_div.width() + 3);
  cover_div.height(original_div.height() + 3);
  cover_div.css("z-index", pin_id);
  cover_div.css("visibility", "visible");
};

add_pin_to_user = function(pin_id) {
  $('.pin-image[pinid="' + pin_id + '"]').addClass('selected');
  $.ajax("/register/api/users/me/coolpins/" + pin_id + "/", {
    type: 'PUT',
    dataType: 'json'
  });
  pin_count += 1;
  if (pin_count > 4) {
    return $('#continue_button').removeAttr('disabled');
  }
};

remove_pin_from_user = function(pin_id) {
  $('.pin-image[pinid="' + pin_id + '"]').removeClass('selected');
  $.ajax("/register/api/users/me/coolpins/" + pin_id + "/", {
    type: 'DELETE',
    dataType: 'json'
  });
  pin_count -= 1;
  if (pin_count < 5) {
    return $('#continue_button').attr('disabled', 'disabled');
  }
};

$("#continue_button").click(function() {
  return window.location.href = '3';
});

$("#skip_button").click(function() {
  var username;
  username = $(this).attr('username');
  return window.location.href = '/' + username;
});
