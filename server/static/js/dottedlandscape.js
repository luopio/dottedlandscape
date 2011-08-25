/* Author: Lauri Kainulainen */

var MOUSEBUTTONDOWN = false;
var ACTIVE_COLOR = [255, 0, 0];

function panelCellPress(e) {
    var x = $(this).attr('x');
    var y = $(this).attr('y');
    if(MOUSEBUTTONDOWN) {
        // log(e)
        // log('pressed '+x+','+y);
        $.post('/a/press', {'x': x, 'y': y, 
                'c': ACTIVE_COLOR}, 
            function(data) {
                log('server said:' + data)    
            })
    }
}

function changeColor(e) {
    var s = $(this).css('background-color');
    s = s.replace(' ', '');
    s = s.split('(')[1].split(')')[0];
    var colors = s.split(',');
    
    ACTIVE_COLOR = [parseInt(colors[0]), parseInt(colors[1]), parseInt(colors[2])];
    log(ACTIVE_COLOR);
}

$(function() {    
    $('#color div').click(changeColor);
    
    $('#panel td').mouseenter(panelCellPress);
    // $('#panel td').bind('touchmove', panelCellPress);
    
    $('body').mousedown(function(e) { MOUSEBUTTONDOWN = true; })
    $('body').bind('touchstart', function(e) { MOUSEBUTTONDOWN = true; })
    $('body').mouseup(function(e) { MOUSEBUTTONDOWN = false; })
    $('body').bind('touchend', function(e) { MOUSEBUTTONDOWN = false; })
    //$('body').bind('touchcancel', function(e) { MOUSEBUTTONDOWN = false; })
    panelUpdater.poll();
    
    var panelWidth = $('#panel').width();
    var panelHeight = $('#panel').height();
    
    /* sending touchmove on one panel tile won't work. Either the element is too
     * small or the element needs to receive touchstart first. Anyway moving a 
     * finger needs to be noticed on top of the whole panel and then find the
     * tile in question
     */
    $('#panel').bind('touchmove',function(e){
        e.preventDefault();
        var touch = e.originalEvent.touches[0] || e.originalEvent.changedTouches[0];
        var elm = $(this).offset();
        var x = touch.pageX - elm.left;
        var y = touch.pageY - elm.top;
        if(x < $(this).width() && x > 0) {
            if(y < $(this).height() && y > 0) {
                var row = Math.round(y / panelHeight * 8) - 1;
                var col = Math.round(x / panelWidth * 8) - 1;
                $.post('/a/press', {'x': col, 'y': row, 
                    'c': ACTIVE_COLOR}, 
                    function(data) {
                        log('server said:' + data)    
                    })
            }
        }
    });
})

/* for some reason simple recursive update function won't work so we'll need to use
 * a separate "static object" for this, which then calls window.setTimeout
 */
var panelUpdater = {
    errorSleepTime: 500,
    
    poll: function() {
        $.ajax({url: "/a/update", dataType: "json", type: "GET",
               success: panelUpdater.onSuccess,
               error: panelUpdater.onError});
    },

    onSuccess: function(data) {
        var counter = 0;
        $('#panel td').each(function (e) { 
            $(this).css('background-color', 'rgb('+data[counter]+','+data[counter+1]+','+data[counter+2]+')');
            $(this).text(counter);
            counter += 3;
        });
        panelUpdater.errorSleepTime = 500;
        window.setTimeout(panelUpdater.poll, 0);
    },

    onError: function(response) {
        panelUpdater.errorSleepTime *= 2;
        log("Poll error; sleeping for", panelUpdater.errorSleepTime, "ms");
        window.setTimeout(panelUpdater.poll, panelUpdater.errorSleepTime);
    },
};




















