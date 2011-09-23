/* Author: Lauri Kainulainen */

/** Provides the functionality for grabbing panel events and sending
 *  them to the server (i.e. provides the input)
 */
var panelInteraction = {
    mouseButtonDown: false,
    activeColor: [255, 0, 0],
    
    // optional init parameter that get's called everytime a cell is painted
    changeCallback: null,
    // if true, no requests are sent to the server
    justLocal: false,
    
    init: function(justLocal, changeCallback) {
        log('panelInteraction: init')
        $('#panel td').mouseenter(panelInteraction.cellPressedEvent);
        $('body').mousedown(panelInteraction.cellPressStartedEvent);
        $('body').bind('touchstart', panelInteraction.cellPressStartedEvent);
        
        $('body').mouseup(function(e) { 
            panelInteraction.mouseButtonDown = false; })
        $('body').bind('touchend', function(e) { 
            panelInteraction.mouseButtonDown = false; })
        
        
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
                    panelInteraction.cellPressedAt(col, row);
                }
            }
        });
        
        /* support changing colors */
        $('#color div').click(panelInteraction.colorSelectionEvent);
        panelInteraction.changeCallback = changeCallback;
        panelInteraction.justLocal = justLocal;
    },
        
    cellPressedEvent: function(e) {
        if(panelInteraction.mouseButtonDown) {
            var x = $(this).attr('x');
            var y = $(this).attr('y');
            panelInteraction.cellPressedAt(x, y);
        }
    },
    
    cellPressedAt: function(x, y) {
        if(panelInteraction.mouseButtonDown) {
            if(!panelInteraction.justLocal) {
                $.post('/a/press', {'x': x, 'y': y, 
                        'c': panelInteraction.activeColor}, 
                    function(data) {
                        // log('server said:' + data)    
                    }
                );
            }
            if(panelInteraction.changeCallback) {
                panelInteraction.changeCallback(x, y, panelInteraction.activeColor);
            }
        }
    },
    
    cellPressStartedEvent: function(e) { 
        panelInteraction.mouseButtonDown = true;
        var $el = $(e.target); // $(this) does not work
        var x = $el.attr('x');
        var y = $el.attr('y');
        if(x && y) {
            panelInteraction.cellPressedAt(x, y); 
        }
    },
    
    colorSelectionEvent: function(e) {
        var s = $(this).css('background-color');
        s = s.replace(' ', '');
        s = s.split('(')[1].split(')')[0];
        var colors = s.split(',');
        panelInteraction.activeColor = [parseInt(colors[0]), parseInt(colors[1]), parseInt(colors[2])];
        log(panelInteraction.activeColor);
    },
    
    playAnimation: function(title) {
        $.get('/a/play-animation', {'title': title}, 
                    function(data) {
                        log('play-animation - server said:' + data)    
                    }
             );
    }
    
};

/* for some reason simple recursive update function won't work so we'll need to use
 * a separate "static object" for this, which then calls window.setTimeout
 */
var panelUpdater = {
    errorSleepTime: 500,
    previousDataPacket: null,
    
    poll: function() {
        $.ajax({url: "/a/update", dataType: "json", type: "GET",
                // ifModified: true, won't call success and thus cut the poll, needs another handler if used
                cache: false,
                success: panelUpdater.onSuccess,
                error: panelUpdater.onError});
    },
    
    init: function() {
        log('panelUpdater: init')
        panelUpdater.poll();
    },

    onSuccess: function(data, status) {
        if(data != panelUpdater.previousDataPacket) {
            var counter = 0;
            $('#panel td').each(function (e) { 
                $(this).css('background-color', 'rgb('+data[counter]+','+data[counter+1]+','+data[counter+2]+')');
                // $(this).text(counter);
                counter += 3;
            });
            panelUpdater.previousDataPacket = data;
        }
        panelUpdater.errorSleepTime = 500;
        window.setTimeout(panelUpdater.poll, 0);
    },

    onError: function(response) {
        panelUpdater.errorSleepTime *= 2;
        log("Poll error; sleeping for", panelUpdater.errorSleepTime, "ms");
        window.setTimeout(panelUpdater.poll, panelUpdater.errorSleepTime);
    },
};
