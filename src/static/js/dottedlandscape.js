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
        log('panelInteraction: init');

        if(!panelInteraction.isInitialized) {
            log('panelInteraction: first bind run');
            $('body').mousedown(panelInteraction.cellPressStartedHandler);
            $('body').bind('touchstart', panelInteraction.cellPressStartedHandler);
            $('body').mouseup(function(e) {
                panelInteraction.mouseButtonDown = false; })
            $('body').bind('touchend', function(e) {
                panelInteraction.mouseButtonDown = false; })
            $('.color-selection div').click(panelInteraction.colorSelectionHandler);
            panelInteraction.isInitialized = true;
        }
        if(element !== null) {
            var $el = $(element);
            panelInteraction.panelWidth = $el.width();
            panelInteraction.panelHeight = $el.height();
            $el.find('td').bind('mouseenter', panelInteraction.cellPressedHandler);
            $el.bind('touchmove', panelInteraction.touchMoveHandler);
        }
        panelInteraction.changeCallback = changeCallback;
        panelInteraction.justLocal = justLocal;
    },

    unBindAll: function() {
        $('td').unbind('mouseenter');
        $('#animate-panel, #text-panel, #draw-panel').unbind('touchmove');
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

        var x = touch.pageX - elm.left;
        var y = touch.pageY - elm.top;

        if(x < panelInteraction.panelWidth && x > 0) {
            if(y < panelInteraction.panelHeight && y > 0) {
                var row = Math.floor(y / panelInteraction.panelHeight * 8);
                var col = Math.floor(x / panelInteraction.panelWidth * 8);
                panelInteraction.cellPressedAt(col, row, $(this));
            }
        }
        return false;
    },

    rgbRegexp: /rgb\(([0-9]+), ?([0-9]+), ?([0-9]+)\)/,
    rgbaRegexp: /rgba\(([0-9]+), ?([0-9]+), ?([0-9]+), ?([0-9]+)\)/,

    cellPressedAt: function(x, y, $el) {
        if(panelInteraction.mouseButtonDown) {
            var color = $el.css('background-color');

            // some use rgba instead of rgb
            var m = panelInteraction.rgbaRegexp.exec(color);
            if(m == null) {
                m = panelInteraction.rgbRegexp.exec(color);
            }
            if(m != null) {
                var r = parseInt(m[1]);
                var g = parseInt(m[2]);
                var b = parseInt(m[3]);
            }

            if( m == null ||
                (r != panelInteraction.activeColor[0] ||
                g != panelInteraction.activeColor[1] ||
                b != panelInteraction.activeColor[2]) ) {

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
        $('div.color-selection').find('div').removeClass('active');
        // set all the color selection divs active
        var klass = $(this).attr('class');
        $('div.color-selection div.'+klass).addClass('active');
        // read the active color
        var s = $(this).css('background-color');
        s = s.replace(' ', '');
        s = s.split('(')[1].split(')')[0];
        var colors = s.split(',');
        panelInteraction.activeColor = [parseInt(colors[0]), parseInt(colors[1]), parseInt(colors[2])];
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
        log('socket.io connection started on ' + new Date().toGMTString());
        var $el = $(element);
        socketIOPanelUpdater.panelCells = $el.find('td');

        socketIOPanelUpdater.socket = io.connect('/');
        log('socket.io connected on ' + new Date().toGMTString());
        socketIOPanelUpdater.socket.on('dl_panel_data', socketIOPanelUpdater.onPanelData);
    },

    onPanelData: function(data) {
        if(data != socketIOPanelUpdater.previousDataPacket) {
            var counter = 0;
            socketIOPanelUpdater.panelCells.each(function (e) {
                $(this).css('background-color', 'rgb('+data[counter]+','+data[counter+1]+','+data[counter+2]+')');
                counter += 3;
            });
            socketIOPanelUpdater.previousDataPacket = data;
        }
    }

};