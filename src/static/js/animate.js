/* Author: Lauri Kainulainen */

var animation = {
    rgbRegexp: /rgb\(([0-9]+), ?([0-9]+), ?([0-9]+)\)/,
    curPlayingFrameIndex: 0,
    animationSpeed: 500,
    selectedFrame: null,
    panelElement: null,
    
    init: function() {
        $('#add-frame').click(animation.addFrame);
        $('#delete-frame').click(animation.removeFrame);
        $('#move-frame-forward').click(animation.moveFrameForward);
        $('#move-frame-backward').click(animation.moveFrameBackward);
        $('#play-button').click(animation.play);
        $('#upload-button').click(animation.upload);
        animation.panelElement = $('#animate-panel');
    },
    
    play: function() {
        var animationFramesData = Array();
        $('div#frames table').each(function(i, el) {
            animationFramesData.push(animation.getFrameData($(el)));
        });
        
        var playRecursion = function() {
            var data = animationFramesData[animation.curPlayingFrameIndex];
            if(!data) {
                animation.curPlayingFrameIndex = 0;
                return
            }
            animation.setPanelData(data);
            animation.curPlayingFrameIndex++;
            window.setTimeout(playRecursion, data.duration * 1000);        
        }
        playRecursion();
    },
    
    addFrame: function(e) {
        if(e)
            e.preventDefault();
            
        var frameLength = $('#frame-length').find('input:checked').val();
        log('frame of len ' + frameLength)
        var $thumb = $('#animate-panel').clone();
        $thumb.attr('id', '').data('duration', frameLength);
        $thumb.find('td').data('x', '').data('y', '');
        $thumb.css('display', 'inline-block');
        $thumb.click(animation.frameSelectedEvent);
        $('div#add-frame').before($thumb);        
    },
    
    getFrameData: function($frameTable) {
        var data = Array();
        $frameTable.find('td').each(function(e) {
            var color = $(this).css('background-color');
            var m = animation.rgbRegexp.exec(color);
            var r = parseInt(m[1]); 
            var g = parseInt(m[2]); 
            var b = parseInt(m[3]);
            data.push(r, g, b);
        });
        return {'data': data, 'duration': $frameTable.data('duration')};
    },
    
    setPanelData: function(frameData) {
        var counter = 0;
        animation.panelElement.find('td').each(function (e) { 
            $(this).css('background-color', 
                'rgb('+frameData.data[counter]+','+frameData.data[counter+1]+','+frameData.data[counter+2]+')');
            counter += 3;
        });
    },
    
    removeFrame: function() {
        el = $('div#frames table').get(animation.selectedFrame);
        animation.unselectFrame();
        $(el).remove();
    },
    
    moveFrameForward: function() {
        if(animation.selectedFrame == $('div#frames table').length - 1) {
            return;
        }
        $('div#frames table').each(function(i, el) {
            $el = $(el);
            if($el.index() == animation.selectedFrame) {
                $el.next().after($el);
                animation.selectedFrame += 1;
                return false;
            }
        })
    },

    moveFrameBackward: function() {
        if(animation.selectedFrame == 0) {
            return;
        }
        $('div#frames table').each(function(i, el) {
            $el = $(el);
            if($el.index() == animation.selectedFrame) {
                $el.prev().before($el);
                animation.selectedFrame -= 1;
                return false;
            }
        })
    },
    
    /*  Changes to the big panel are done here. We get the chance to directly update the small panels
        as well if needed */
    panelChangedCallback: function(x, y, c) {
        log('panel changed')
        var i = parseInt(x) + parseInt(y) * 8;
        $($('#animate-panel td')[i]).css('background-color', 'rgb('+c[0]+','+c[1]+','+c[2]+')');
        if(animation.selectedFrame !== null) {
            var selectedFrameTable = $('div#frames table').get(animation.selectedFrame);
            var affectedPixel = $(selectedFrameTable).find('td').get(i);
            $(affectedPixel).css('background-color', 'rgb('+c[0]+','+c[1]+','+c[2]+')');    
        }
    },
    
    unselectFrame: function() {
        $('div#frames table').removeClass('selected-frame');
        animation.selectedFrame = null;
        $('#frame-move-controls').slideUp();
    },
    
    frameSelectedEvent: function(e) {
        if($(this).hasClass('selected-frame')) {
            animation.unselectFrame();
            return;
        }
        var indx = $(this).index();
        animation.selectedFrame = indx;
        $(this).parent().children().removeClass('selected-frame');
        $(this).addClass('selected-frame');
        $('#frame-move-controls').slideDown();
        $('#slider').slider('value', $(this).data('duration'));
        animation.setPanelData(animation.getFrameData($(this)));
    },
    
    frameLengthChangedEvent: function(value) {
        if(animation.selectedFrame === null) { return; }
        $('div#frames table.selected-frame').data('duration', value);
    },
    
    upload: function() {
        
        if(!$('#animation-title').val()) {
            alert('Please enter a name for your piece.');
            return;            
        }
        if(!$('#animation-author').val()) {
            alert('Please enter your real or artist name.');
            return;
        }
        // get the frame data
        var animationFramesData = Array();
        $('div#frames table').each(function(i, el) {
            animationFramesData.push(animation.getFrameData($(el)));
        });
        if(animationFramesData.length < 1) {
            alert('But there are no frames in your animation..');
            return;
        }
        $.post('/a/save-animation', 
            {   data: animationFramesData, 
                channels: 3,
                title: $('#animation-title').val(), 
                author: $('#animation-author').val() }, 
            function(data) {
                //log('save animation: server said:' + data)
                if(data && data.status == 'ok') {
                    alert('Animation has been saved as '+data.name+
                    ' on the server! You can now play it in the Paint view.')
                }  
            }, 
            'json'
        );
    }
}
