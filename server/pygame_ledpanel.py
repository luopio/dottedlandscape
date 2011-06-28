import pygame, time, sys

import blip_receiver

led_panel_initialized = False
clock, screen = None, None
leds_x, leds_y, amount_of_channels = 0, 0, 0
circle_radius = 6
circle_spacing = 10
window_margins = (30, 30)

def on_receive(header_data, data):
    global led_panel_initialized, leds_x, leds_y
    h, w = header_data[1], header_data[2]
    if not led_panel_initialized or leds_x != w or leds_y != h:
        global screen, clock, amount_of_channels
        width, height = w, h
        amount_of_channels = header_data[3]
        print "Panel: received new width, height", w, h, "on %s channels" % amount_of_channels
        
        pygame.init()
        # get the panel size and set the window width accordingly
        leds_x, leds_y = w, h
        width, height = w * circle_radius + w * circle_spacing + 2 * window_margins[0], \
                        h * circle_radius + h * circle_spacing + 2 * window_margins[1]
        screen = pygame.display.set_mode((width, height)) # , pygame.OPENGL)
         
        pygame.display.set_caption("LED Panel Sim %sx%s" % (w, h) )
        clock = pygame.time.Clock()
        led_panel_initialized = True
    
    evt = pygame.event.Event(pygame.USEREVENT, {'data': data})
    try:
        pygame.event.post(evt)
    except pygame.error:
        print "skip frame"
        pygame.event.clear()


print "Panel: waiting for connections to determine panel size" 
b = blip_receiver.BlipReceiver()
b.add_observer(on_receive)
b.start()

try:
    while not led_panel_initialized:
        time.sleep(0.5)
except KeyboardInterrupt:     
    b.stop()
    sys.exit(1)

done = False 
while done == False:
    # limit cpu usage (max 10 frames per second)
    # clock.tick(100)
     
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # user clicked close
            print "Panel: quit called. Have a good day!"
            done = True
            
        elif event.type  == pygame.USEREVENT:
            # print "received user event"
            screen.fill((0, 0, 0))
            for i in xrange(0, leds_x * leds_y):
                x = (i * amount_of_channels % leds_x) * (circle_radius + circle_spacing) + window_margins[0]
                y = (i * amount_of_channels / leds_x) * (circle_radius + circle_spacing) + window_margins[1]
                if amount_of_channels == 1:
                    rgb = [event.data[i], 0, 0]
                elif amount_of_channels == 3:
                    rgb = [event.data[i], event.data[i+1], event.data[i+2]]
                
                pygame.draw.circle(screen, rgb, [x, y], circle_radius, 0)
        
            pygame.display.flip()

# Be IDLE friendly
b.stop()
pygame.quit ()