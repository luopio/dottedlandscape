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
            if(e.preventDefault) { e.preventDefault(); }
            var touch = e.originalEvent.touches.item(0);
            var elm = $(this).offset();
            var x = touch.clientX - elm.left; 
            var y = touch.clientY - elm.top;
            /*
            var x = touch.pageX - elm.left;
            var touch = e.originalEvent.touches[0] || e.originalEvent.changedTouches[0];
            var y = touch.pageY - elm.top;
            */
            // $('footer').text(x + ", " + y + " panel=" + panelWidth+", "+panelHeight)
            if(x < panelWidth && x > 0) {
                if(y < panelHeight && y > 0) {
                    var row = Math.floor(y / panelHeight * 8);
                    var col = Math.floor(x / panelWidth * 8);
                    //$('footer').text(x + ", " + y + " panel=" + panelWidth+", "+panelHeight + 
                    //    "col, row="+col+", "+ row +" mousedown? "+panelInteraction.mouseButtonDown);
                    /*
                    var cellWidth = panelWidth / 8;
                    var cellHeight = panelHeight / 8;
                    var cellLeftEdgeDelta = x - col * cellWidth;
                    var cellTopEdgeDelta = y - row * cellHeight;
                    */                    
                    // alert('deltas: ' + cellLeftEdgeDelta + ", " + cellTopEdgeDelta+' w/h ' + cellWidth + ", " + cellHeight);
                    //if (cellLeftEdgeDelta > cellWidth * 0.1 && cellLeftEdgeDelta < cellWidth * 0.9) {
                    //    if (cellTopEdgeDelta > cellHeight * 0.1 && cellTopEdgeDelta < cellHeight * 0.9) {
                            panelInteraction.cellPressedAt(col, row);
                    //    }
                    //}
                    
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
            var x = $(this).data('x');
            var y = $(this).data('y');
            panelInteraction.cellPressedAt(x, y);
        }
    },
    
    cellPressedAt: function(x, y) {
        if(panelInteraction.mouseButtonDown) {
            if(!panelInteraction.justLocal) {
                $.post('/a/press', {'x': x, 'y': y, 
                        'c': panelInteraction.activeColor}, 
                    function(data) {
                        // $('footer').text("OK");
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
        var x = $el.data('x');
        var y = $el.data('y');
        if($.isNumeric(x) && $.isNumeric(y)) {
            panelInteraction.cellPressedAt(x, y); 
        }
    },
    
    colorSelectionEvent: function(e) {
        $(this).parent().find('div').removeClass('active');
        $(this).addClass('active');
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
        log('panelUpdater: init');
        $.ajax({url: "/a/update", dataType: "json", type: "GET",
                cache: false,
                data: {'sync': 1},
                success: panelUpdater.onSuccess,
                error: panelUpdater.onError});
        // panelUpdater.poll();
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
