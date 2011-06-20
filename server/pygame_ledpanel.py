import pygame, time, sys

import blip_receiver

led_panel_initialized = False
clock, screen = None, None
leds_x, leds_y = 0, 0
circle_radius = 6
circle_spacing = 10
window_margins = (30, 30)

def on_receive(header_data, data):
    global led_panel_initialized, leds_x, leds_y
    h, w = header_data[1], header_data[2]
    if not led_panel_initialized or leds_x != w or leds_y != h:
        print "Panel: received new width, height", w, h
        global screen, clock
        width, height = w, h
        
        pygame.init()
        # get the panel size and set the window width accordingly
        leds_x, leds_y = w, h
        width, height = w * circle_radius + w * circle_spacing + 2 * window_margins[0], \
                        h * circle_radius + h * circle_spacing + 2 * window_margins[1]
        screen = pygame.display.set_mode((width, height))
         
        pygame.display.set_caption("LED Panel Sim %sx%s" % (w, h) )
        clock = pygame.time.Clock()
        led_panel_initialized = True
    
    evt = pygame.event.Event(pygame.USEREVENT, {'data': data})
    pygame.event.post(evt)
    

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
    clock.tick(10)
     
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # user clicked close
            print "Panel: quit called. Have a good day!"
            done = True
            
        elif event.type  == pygame.USEREVENT:
            # print "received user event"
            screen.fill((0, 0, 0))
            for i in xrange(0, leds_x * leds_y):
                x = (i % leds_x) * (circle_radius + circle_spacing) + window_margins[0]
                y = (i / leds_x) * (circle_radius + circle_spacing) + window_margins[1]
                val = event.data[i]
                
                pygame.draw.circle(screen, (val, 100, 10), [x, y], circle_radius, 0)
        
            pygame.display.flip()

# Be IDLE friendly
b.stop()
pygame.quit ()