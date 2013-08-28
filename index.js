$(function() {
    $.ajax({
        url: '/tasks.js',
        success: function(data) {
            $.each(data, function(i, elem) {
                var sym = elem[0], name = elem[1];
                $('<option>').attr('value', sym).text(sym + ' - ' + name).appendTo($('[name=tasks]'));
            })
        },
        dataType: 'json'
    });
})

var cached = [];

function load_msg() {
    var ident = location.hash.slice(1)
    $.ajax({
        url: '/' + ident + '.' + cached.length + '.wait.js',
        success: function(data) {
            var seen_end = false
            $.each(data, function(i, item) {
                if(item.type == 'end') seen_end = true
                if(i < cached.length) return
                var elem = $('<div class=ev>')
                elem.addClass('ev-' + item.type).text(item.val)
                elem.hide()
                elem.appendTo('#events')
                elem.show('slow')
            });
            if(cached.length != 0)
                $("html, body").animate({ scrollTop: $(document).height()},
                                        { duration: "slow", queue: false });
            cached = data
            if(!seen_end)
                setTimeout(load_msg, 200)
        },
        dataType: 'json'
    });
}

$(load_msg);

function make_sizes() {
    var size = ($(window).height()
                    - $('.body').height() - 100)
    console.log($('html').css('height'), size)
    $('#events').css('height', size + 'px')
}

$(make_sizes)
$(window).resize(make_sizes)
