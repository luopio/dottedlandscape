import datetime
import wx


class LEDPanelFrame(wx.Frame): 
    """a frame that imitates a led panel"""

    def __init__(self, parent=None, id=-1, title=None): 
        # wx.Frame.__init__(self, parent, id, title)
        super(LEDPanelFrame, self).__init__(parent, id, title)
        self.w = 0
        self.h = 0
        self.led_initialized = False
        self.panel = wx.Panel(self, size=(200, 200)) 
        self.panel.Bind(wx.EVT_PAINT, self.on_paint) 
        self.statusbar = wx.StaticText(parent=self.panel, pos=(20, 450))
        self.Fit() 

    def on_paint(self, event):
        # establish the painting surface
        dc = wx.PaintDC(self.panel)
        # dc.SetPen(wx.Pen('blue', 4))
        # draw a blue line (thickness = 4)
        # dc.DrawLine(50, 20, 300, 20)
        # dc.SetPen(wx.Pen('red', 1))
        # draw a red rounded-rectangle
        # rect = wx.Rect(50, 50, 100, 100) 
        # dc.DrawRoundedRectangleRect(rect, 8)
        # draw a red circle with yellow fill
        # dc.SetBrush(wx.Brush('yellow'))
        # print "paint"
        # dc.SetBrush(wx.Brush((255, 10, 30 * int(datetime.datetime.now().strftime('%S')))))
        print "paint!"
        margins = (40, 40)
        for i in xrange(0, self.w * self.h):
            x = i % self.w * 50 + margins[0]
            y = i / self.w * 50 + margins[1]
            r = 20
            val = self.data[i]

            dc.SetBrush(wx.Brush((val, 10, 10)))
            dc.DrawCircle(x, y, r)
        # self.statusbar.SetLabel(label=datetime.datetime.now().strftime('%H:%M:%S'))
    
    def on_receive(self, header_data, data):
        if not self.led_initialized:
            w, h = header_data[1], header_data[2]
            print "widhtheight", w, h
            self.SetSize((w * 10, h * 10))
            self.led_initialized = True
        self.data = data
        print "got data", data
        self.Update() # to refresh the panel


app = wx.PySimpleApp()
frame = LEDPanelFrame(title='Waiting for connections..')
frame.Center()
frame.Show()

import blip_receiver
b = blip_receiver.BlipReceiver()
b.add_observer(frame.on_receive)
b.start()

app.MainLoop()
