
// set the format you want your pop-up calendars date to be in
$('.datepicker').datepicker({ format: 'yyyy-mm-dd' });

//-------------------------------------------------------------------------
// TOGGLE HIDDEN FORM WHEN 'EDIT POST' BUTTON IS CLICKED
//-------------------------------------------------------------------------
// function for showing/hiding the formset for upcoming-posts/drafts
$(function() {
    $('.upcoming_formset_table').hide(); // hide all forms by default
    $('.upcoming_btn').click(function(){
        var t = $(this);
        t.parent().next('.upcoming_formset_table').toggle('fast', function(){
            var klass = ($(this).is(':hidden')) ? 'btn btn-small' : 'btn btn-inverse btn-small';
            var txt   = ($(this).is(':hidden')) ? 'Edit Post' : 'Hide Post';
            t.attr('class', klass);
            t.html(txt);
        });
    })
});

//-------------------------------------------------------------------------
// COUNTDOWN FUNCTIONALITY FOR LIVE TIMEDELTA
//-------------------------------------------------------------------------
// use moment.js to set the default fields for the time inputs
// also create a function that update every second and displays
// the Facebook scheduled_post feature's cutoff date.
var now = moment();
var time_helper = $('#time_helper');
var update = function() {
    var ten_minutes = moment(new Date())
        .add('minutes', 10)
        .format('MMMM Do YYYY, h:mm:ss a');

    time_helper.text('If your post date falls before \
        '+ten_minutes+', then it will be sent immediatley.');
};
update();
setInterval(update, 1000);

// add the default time values to the post date fields
$('#id_post_date_1').val(now.format("h"));
$('#id_post_date_2').val(now.format("mm"));
$('#id_post_date_3 option[value="'+now.format("a").toUpperCase()+'"]')
    .attr('selected', 'selected');

//-------------------------------------------------------------------------
// FETCH INFO FOR FACEBOOK FROM 3RD PARTY SITES
//-------------------------------------------------------------------------
// detect when a user pastes a URL into the message input form
// or when they press the space bar, to see if they typed a URL
$('#id_message').on({
    keydown: function(evt) {
        if (evt.keyCode == 32) getUrl($(this).val());
    },
    paste: function() {
        var el = $(this);
        setTimeout(function() {
            var txt = $(el).val();
            getUrl(txt);
        }, 0);
    }
});

// function extracts a url from out of some text
function getUrl(txt) {
    var regexp = new RegExp('(ftp|http|https)://[a-z0-9\-_]+(\.[a-z0-9\-_]+)+([a-z0-9\-\.,@\?^=%&;:/~\+#]*[a-z0-9\-@\?^=%&;/~\+#])?', 'i');

    if (regexp.test(txt)) {
        var url = txt.match(regexp);
        urlToDjango(url[0]);
    }
};

// setup the AJAX functioniality for sending the text to Django
function urlToDjango(item) {
    $.getJSON(
        "{{ request.get_full_path }}json",
        {"url": item},
        function(x) {
            var html_output = x['html_output'];
            $('#id_message').after(html_output).fadeIn();
        }
    )
    .fail(function() { console.log('fail-function ')});
};

function isValidURL(url){
    var regx = /(ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/;

    if(regx.test(url)) return true;
    else return false;
}

//-------------------------------------------------------------------------
// HANDLE AJAX REQUEST
//-------------------------------------------------------------------------
// when a user hits the save button when editing an existing
// post in the upcoming posts area, this function will grab
// the information about this forms id from the html id tag
// and then it will pass that info to the update_post function
$('.update_post_btn').click(function(elem) {
    elem.preventDefault();
    update_post($(this)); // create the AJAX request
});

// setup the AJAX functioniality for updating a post queue form
function update_post(self) {

    var mydata   = self.closest("form").serialize(),
        btn_type = self.attr('name'),
        form_id  = self.attr('data');

    // add the button that was pushed to the data
    mydata = mydata + '&btn_type=' + btn_type

    $.ajax({
        type: 'POST',
        url: '/social/post/edit/'+form_id+'/',
        data: mydata,
        crossDomain: false,
        xhrFields: { "X-CSRFToken": "{{ csrf_token }}" },
        success: function(ctx) {
            // check if they deactivated a post and sent it to drafts
            // and if so remove it so that they don't edit the same form again
            $('#upcoming_form_'+form_id).remove();

            // TODO:
            // move the success message out of the form, as the user will
            // be unable to see if they hit 'deactivate'

            // render the success message
            $('#form_message_'+form_id)
                .html('<div class="control-group success">'+
                '<span class="help-inline">'+
                '<strong>Your post was updated!</strong>'+
                '</span></div>').show().fadeOut(9000);
        },
        dataType: 'json',
        fail: function(err) { console.log(err); }
    });

};

//----------------------------------------------------------------------------
//
//----------------------------------------------------------------------------
// http://brack3t.com/ajax-and-django-views.html

function apply_form_field_error(fieldname, error) {
    // takes a field name and an error and finds the field on the page
    // and sets the error text to the passed-in error.
    var input     = $("#id_" + fieldname),
        container = $("#div_id_" + fieldname),
        error_msg = $("<span />").addClass("help-inline ajax-error").text(error[0]);

    container.addClass("error");
    error_msg.insertAfter(input);
}

function clear_form_field_errors(form) {
    // removes the above text and classes, resetting the form.
    // prevents doubled-up errors by running this script before each
    // AJAX request. Add to JQuery's beforeSend if you don't want to
    // think about it
    $(".ajax-error", $(form)).remove();
    $(".error", $(form)).removeClass("error");
}

/*
function django_message(msg, level) {
    var levels = {
        warning: 'alert',
        error:   'error',
        success: 'success',
        info:    'info'
    },
    source = $('#message_template').html(),
    template = Handlebars.compile(source),
    context = {
        'tags':    levels[level],
        'message': msg
    },
    html = template(context);
    $("#message_area").append(html);
}

function django_block_message(msg, level) {
    var source   = $("#message_block_template").html(),
        template = Handlebars.compile(source),
        context  = {level: level, body: msg},
        html     = template(context);

    $("#message_area").append(html);
}
*/
