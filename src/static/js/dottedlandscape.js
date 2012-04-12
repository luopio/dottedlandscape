/* Author: Lauri Kainulainen */
/** Provides the functionality for grabbing panel events and sending
 *  them to the server (i.e. provides the input)
 */
var panelInteraction = {
    mouseButtonDown: false,
    activeColor: [255, 0, 0],
    useSocketIO: true,
    
    // optional init parameter that get's called everytime a cell is painted
    changeCallback: null,
    // if true, no requests are sent to the server
    justLocal: false,
    isInitialized: false,

    bind: function(element, justLocal, changeCallback) {
        log('panelInteraction: init')

        if(!panelInteraction.isInitialized) {
            $('body').mousedown(panelInteraction.cellPressStartedHandler);
            $('body').bind('touchstart', panelInteraction.cellPressStartedHandler);
            $('body').mouseup(function(e) {
                panelInteraction.mouseButtonDown = false; })
            $('body').bind('touchend', function(e) {
                panelInteraction.mouseButtonDown = false; })
            $('.color-changer div').click(panelInteraction.colorSelectionHandler);
            panelInteraction.isInitialized = true;
        }
        if(element !== null) {
            var $el = $(element);
            $el.find('td').mouseenter(panelInteraction.cellPressedHandler);
            panelInteraction.panelWidth = $el.width();
            panelInteraction.panelHeight = $el.height();

            $el.bind('touchmove', panelInteraction.touchMoveHandler);
        }
        panelInteraction.changeCallback = changeCallback;
        panelInteraction.justLocal = justLocal;
    },

    unBindAll: function() {
        $('td').unbind('mouseenter');
        $('div#animate, div#text, div#draw').unbind('touchmove');
    },

    cellPressedHandler: function(e) {
        if(panelInteraction.mouseButtonDown) {
            var x = $(this).data('x');
            var y = $(this).data('y');
            panelInteraction.cellPressedAt(x, y, $(this));
        }
    },

    /* sending touchmove on one panel tile won't work. Either the element is too
     * small or the element needs to receive touchstart first. Anyway moving a
     * finger needs to be noticed on top of the whole panel and then find the
     * tile in question
     */
    touchMoveHandler: function(e){
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
        if(x < panelInteraction.panelWidth && x > 0) {
            if(y < panelInteraction.panelHeight && y > 0) {
                var row = Math.floor(y / panelInteraction.panelHeight * 9);
                var col = Math.floor(x / panelInteraction.panelWidth * 12);
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
                panelInteraction.cellPressedAt(col, row, $(this));
                //    }
                //}

            }
        }
    },

    rgbRegexp: /rgb\(([0-9]+), ?([0-9]+), ?([0-9]+)\)/,

    cellPressedAt: function(x, y, $el) {
        if(panelInteraction.mouseButtonDown) {
            var color = $el.css('background-color');
            var m = panelInteraction.rgbRegexp.exec(color);
            var r = parseInt(m[1]);
            var g = parseInt(m[2]);
            var b = parseInt(m[3]);
            if( r != panelInteraction.activeColor[0] ||
                g != panelInteraction.activeColor[1] ||
                b != panelInteraction.activeColor[2]) {

                if(!panelInteraction.justLocal) {
                    socketIOPanelUpdater.socket.emit('panel_press', {'x': x, 'y': y,
                        'c': panelInteraction.activeColor} );
                }
                if(panelInteraction.changeCallback) {
                    panelInteraction.changeCallback(x, y, panelInteraction.activeColor);
                }
            }
        }
    },
    
    cellPressStartedHandler: function(e) {
        panelInteraction.mouseButtonDown = true;
        var $el = $(e.target); // $(this) does not work
        var x = $el.data('x');
        var y = $el.data('y');
        if( !isNaN(parseInt(x)) && !isNaN(parseInt(y)) ) {
            panelInteraction.cellPressedAt(x, y, $el);
        }
    },
    
    colorSelectionHandler: function(e) {
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


var socketIOPanelUpdater = {
    socket: null,
    previousDataPacket: null,
    panelCells: [],

    bind: function(element) {
        var $el = $(element);
        socketIOPanelUpdater.panelCells = $el.find('td');
        socketIOPanelUpdater.socket = io.connect('/');
        socketIOPanelUpdater.socket.on('dl_panel_data', socketIOPanelUpdater.onSuccess);
    },

    onSuccess: function(data) {
        if(data != socketIOPanelUpdater.previousDataPacket) {
            var counter = 0;
            socketIOPanelUpdater.panelCells.each(function (e) {
                $(this).css('background-color', 'rgb('+data[counter]+','+data[counter+1]+','+data[counter+2]+')');
                // $(this).text(counter);
                counter += 3;
            });
            socketIOPanelUpdater.previousDataPacket = data;
        }
    }

};