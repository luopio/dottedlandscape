import pygame, time

import blip_receiver

led_panel_initialized = False
clock, screen = None, None
leds_x, leds_y = 0, 0
width, height = 0, 0

def on_receive(header_data, data):
    global led_panel_initialized
    if not led_panel_initialized:
        h, w = header_data[1], header_data[2]
        print "Received width, height", w, h
        global width, height, screen, clock, leds_x, leds_y
        width, height = w, h
        
        pygame.init()
        # Set the height and width of the screen
        # width, height = 200, 200
        leds_x, leds_y = w, h
        width, height = w * 40, h * 40
        screen = pygame.display.set_mode((400, 400))
         
        pygame.display.set_caption("LED Panel Sim")
        clock = pygame.time.Clock()
        led_panel_initialized = True
    
    # print "got data", data
    evt = pygame.event.Event(pygame.USEREVENT, {'data': data})
    pygame.event.post(evt)
    

print "Waiting for connections to determine panel size" 
b = blip_receiver.BlipReceiver()
b.add_observer(on_receive)
b.start()

while not led_panel_initialized:
    time.sleep(0.5)

done = False 
while done == False:
    # limit cpu usage (max 10 frames per second)
    clock.tick(10)
     
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # user clicked close
            print "Quit called. Have a good day!"
            done = True
            
        elif event.type  == pygame.USEREVENT:
            # print "received user event"
            screen.fill((0, 0, 0))
            margins = (30, 30)
            r = 6
            for i in xrange(0, leds_x * leds_y):
                x = (i % leds_x) * 20 + margins[0]
                y = (i / leds_x) * 20 + margins[1]
                val = event.data[i]
                
                pygame.draw.circle(screen, (val, 100, 10), [x, y], r, 0)
        
            pygame.display.flip()

print "stopping receiver"
# Be IDLE friendly
b.keep_on_truckin = False
b.join()
pygame.quit ()