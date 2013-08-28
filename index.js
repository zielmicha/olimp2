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
            cached = data
            if(!seen_end)
                setTimeout(load_msg, 200)
        },
        dataType: 'json'
    });
}

$(load_msg);
