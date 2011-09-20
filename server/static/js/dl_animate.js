/* Author: Lauri Kainulainen */

var animation = {
    frames: Array(),
    rgbRegexp: /rgb\(([0-9]+), ?([0-9]+), ?([0-9]+)\)/,
    curPlayingFrameIndex: 0,
    animationSpeed: 500,
    
    init: function() {
        $('div#add-frame').click(animation.addFrame);    
    },
    
    play: function() {
        var data = animation.frames[animation.curPlayingFrameIndex];
        if(!data) {
            animation.curPlayingFrameIndex = 0;
            return
        }
        var counter = 0;
        $('#panel td').each(function (e) { 
            $(this).css('background-color', 'rgb('+data[counter]+','+data[counter+1]+','+data[counter+2]+')');
            counter += 3;
        });
        animation.curPlayingFrameIndex++;
        window.setTimeout(animation.play, animation.animationSpeed);
    },
    
    addFrame: function(e) {
        if(e)
            e.preventDefault();
            
        var data = Array();
        
        $('#panel td').each(function(e) {
            var color = $(this).css('background-color');
            var m = animation.rgbRegexp.exec(color);
            var r = parseInt(m[1]); 
            var g = parseInt(m[2]); 
            var b = parseInt(m[3]);
            data.push(r, g, b);
        });
        var $thumb = $('#panel').clone();
        $thumb.attr('id', '').attr('frame-index', animation.frames.length);
        $thumb.find('td').width(5).height(5).attr('x', '').attr('y', '');
        $thumb.css('display', 'inline-block');
        $thumb.click(animation.frameSelectedEvent);
        // create line-breaks to support longer timelines
        if(animation.frames.length % 8 == 0) {
            $('div#add-frame').before(document.createElement('br'));        
        }
        $('div#add-frame').before($thumb);        
        animation.frames.push(data);
        log(animation.frames.length + '. frame added with length ' + data.length);
    },
    
    removeFrame: function() {
        
    },
    
    panelChangedCallback: function(x, y, c) {
        var i = parseInt(x) + parseInt(y) * 8;
        $($('#panel td')[i]).css('background-color', 'rgb('+c[0]+','+c[1]+','+c[2]+')');
    },
    
    frameSelectedEvent: function(e) {
        var indx = $(this).attr('frame-index');
        $(this).parent().children().removeClass('selected-frame');
        $(this).addClass('selected-frame');
    },
    
    upload: function() {
        if(animation.frames.length < 1) {
            alert('But there are no frames in your animation..');
            return;
        }
        if(!$('#animation-title').val()) {
            alert('Please enter a name for your piece.');
            return;            
        }
        if(!$('#animation-author').val()) {
            alert('Please enter your real or artist name.');
            return;
        }
        $.post('/a/save-animation', 
            { data: animation.frames, channels: 3, speed: animation.animationSpeed,
              title: $('#animation-title').val(), author: $('#animation-author').val() }, 
            function(data) {
                log('save animation: server said:' + data)
                if(data && data != 'FAIL') {
                    alert('Animation saved! You can now play it in the Live view.')
                }    
            }, 
            'json'
        );
    }
}
