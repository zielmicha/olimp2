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
            cached = data
            $.each(data, function(i, elem) {
                if(elem.type == 'end') seen_end = true
                $('<div class=ev>').addClass('ev-' + elem.type).text(elem.val).appendTo('#events')
            });
            if(!seen_end)
                setTimeout(load_msg, 200)
        },
        dataType: 'json'
    });
}

$(load_msg);
