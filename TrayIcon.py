# -*- coding: utf-8 -*-
import Tkinter
import platform
import types
import os
#import TkTray
import Winico

_platform = platform.system()

# ToolTip class, taken from the tkinter wiki, with the coords() method
# modified for use with tray icons;
# winico icons have a built-in tooltip which is mandatory,
# to be compatible, we need to create our own tooltips on X
class ToolTip:
    def __init__(self, master, text='Your text here', delay=1500, **opts):
        self.master = master
        self._opts = {'anchor':'center', 'bd':1, 'bg':'lightyellow', 'delay':delay, 'fg':'black',\
                      'follow_mouse':0, 'font':None, 'justify':'left', 'padx':4, 'pady':2,\
                      'relief':'solid', 'state':'normal', 'text':text, 'textvariable':None,\
                      'width':0, 'wraplength':150}
        self.configure(**opts)
        self._tipwindow = None
        self._id = None
        self._id1 = self.master.bind("<Enter>", self.enter, '+')
        self._id2 = self.master.bind("<Leave>", self.leave, '+')
        self._id3 = self.master.bind("<ButtonPress>", self.leave, '+')
        self._follow_mouse = 0
        if self._opts['follow_mouse']:
            self._id4 = self.master.bind("<Motion>", self.motion, '+')
            self._follow_mouse = 1

    def configure(self, **opts):
        for key in opts:
            if self._opts.has_key(key):
                self._opts[key] = opts[key]
            else:
                KeyError = 'KeyError: Unknown option: "%s"' %key
                raise KeyError

    ##----these methods handle the callbacks on "<Enter>", "<Leave>" and "<Motion>"---------------##
    ##----events on the parent widget; override them if you want to change the widget's behavior--##

    def enter(self, event=None):
        self._schedule()

    def leave(self, event=None):
        self._unschedule()
        self._hide()

    def motion(self, event=None):
        if self._tipwindow and self._follow_mouse:
            x, y = self.coords()
            self._tipwindow.wm_geometry("+%d+%d" % (x, y))

    ##------the methods that do the work:---------------------------------------------------------##

    def _schedule(self):
        self._unschedule()
        if self._opts['state'] == 'disabled':
            return
        self._id = self.master.after(self._opts['delay'], self._show)

    def _unschedule(self):
        id = self._id
        self._id = None
        if id:
            self.master.after_cancel(id)

    def _show(self):
        if self._opts['state'] == 'disabled':
            self._unschedule()
            return
        if not self._tipwindow:
            self._tipwindow = tw = Tkinter.Toplevel(self.master)
            # hide the window until we know the geometry
            tw.withdraw()
            tw.wm_overrideredirect(1)

            if tw.tk.call("tk", "windowingsystem") == 'aqua':
                tw.tk.call("::tk::unsupported::MacWindowStyle", "style", tw._w, "help", "none")

            self.create_contents()
            tw.update_idletasks()
            x, y = self.coords()
            tw.wm_geometry("+%d+%d" % (x, y))
            tw.deiconify()

    def _hide(self):
        tw = self._tipwindow
        self._tipwindow = None
        if tw:
            tw.destroy()
    ##----these methods might be overridden in derived classes:----------------------------------##

    def coords(self):
        # The tip window must be completely outside the master widget;
        # otherwise when the mouse enters the tip window we get
        # a leave event and it disappears, and then we get an enter
        # event and it reappears, and so on forever :-(
        x0, y0, x1, y1 = self.master.bbox()
        tw = self._tipwindow
        twx, twy = tw.winfo_reqwidth(), tw.winfo_reqheight()
        w, h = tw.winfo_screenwidth(), tw.winfo_screenheight()
        # as x coord simply use x0, just make sure we're inside the screen
        if x0 < 0:
            x0 = 0
        elif x0 + twx > w:
            x0 = w - twx
        # now calculate y
        if y0 > w / 2:
            # assume the panel is at the bottom of the screen, so put the tooltip
            # above the tray icon
            y = y0 - twy - 3
        else:
            # panel at the top of the screen, put the tooltip below the tray icon
            y = y1 + 3
        return x0, y

    def create_contents(self):
        opts = self._opts.copy()
        for opt in ('delay', 'follow_mouse', 'state'):
            del opts[opt]
        label = Tkinter.Label(self._tipwindow, **opts)
        label.pack()

########################################################################

class Icon:
    def __init__(self, image=None, ico=None, tooltip='Your text here', menu=True, command=None):
        '''Platform-independent Tray-icon wrapper. Options:
        image     - may be either a filename of a gif image file (or any other
                    image format supported by Tk) or a string of base64
                    encoded image data or a PhotoImage object to use with TkTray
        ico       - pathname to an .ico file to use with winico
        tooltip   - text shown in a tooltip when the mouse enters the icon
        menu      - a boolean that determines whether the icon should have an
                    associated context menu. If True, this menu can be accessed
                    through the icon's menu attribute
        command   - optional Python command that will be executed when the left
                    mouse button is pressed on the icon; the x- and y-coordinates
                    of the event will be passed to that command.'''
        self.master = Tkinter._default_root
        if not self.master:
            raise RuntimeError, 'Too early to create tray icon.'

        if menu:
            self.menu = Tkinter.Menu(self.master, tearoff=0)
        else:
            self.menu = None

        if _platform == 'Windows':
            self.image = None
            self.icon = Winico.Icon(ico)
            if self.menu:
                def _do_command_win(eventtype, x, y):
                    if eventtype == "WM_RBUTTONDOWN":
                        self.menu.tk_popup(x, y)
                    elif command and eventtype == "WM_LBUTTONDOWN":
                        command(x, y)
                func = self.master.register(_do_command_win)
                self.icon.taskbar_add(text=tooltip, callback=(func, '%m', '%x', '%y'))
            else:
                self.icon.taskbar_add(text=tooltip)
        else:
            if type(image) in types.StringTypes:
                if os.path.isfile(image):
                    self.image = Tkinter.PhotoImage(file=image)
                else:
                    self.image = Tkinter.PhotoImage(data=image)
            else:
                self.image = image
            #self.icon = TkTray.Icon(self.master, image=self.image) not building for non windows
            if self.menu:
                self.icon.bind('<3>', self._context_menu_x)
            if command:
                def _do_command_x(event):
                    command(event.x_root, event.y_root)
                self.icon.bind('<1>', _do_command_x)
            # new versions of tktray have a balloon command built in, but it
            # did not work here with most WMs and isn't trivial to set up either,
            # so for now we better stick with our tooltips here
            ToolTip(self.icon, text=tooltip)

    def _context_menu_x(self, event):
        if self.menu:
            w, h = self.menu.winfo_reqwidth(), self.menu.winfo_reqheight()
            x0, y0, x1, y1 = self.icon.bbox()
            # get the coords for the popup menu; we want it to the mouse pointer's
            # left and above the pointer in case the taskbar is on the bottom of the
            # screen, else below the pointer; add 1 pixel towards the pointer in each
            # dimension, so the pointer is '*inside* the menu when the button is being
            # released, so the menu will not unpost on the initial button-release event
            if y0 > self.icon.winfo_screenheight() / 2:
                # assume the panel is at the bottom of the screen
                x, y = event.x_root - w + 1, event.y_root - h + 1
            else:
                x, y = event.x_root - w + 1, event.y_root - 1
            # make sure that x is not outside the screen
            if x < 5:
                x = 5
            self.menu.tk_popup(x, y)

    def coords(self):
        if _platform == 'Windows':
            return None
        else:
            return self.icon.bbox()

    def destroy(self):
        self.icon.destroy()

    def destroy_all(self):
        self.destroy()
        if _platform == 'Windows':
            self.icon.delete_all()

########################################################################
def test():
    import sys, tkMessageBox
    root = Tkinter.Tk()
    root.withdraw()
    root.protocol("WM_DELETE_WINDOW", root.withdraw)
    def cmd(x,y):
        print 'Received Button-1 event at coords: x:', x, 'y:', y
        root.deiconify()
    def info():
        tkMessageBox.showinfo(message='Trayicon widget demo.')
    icon = Icon(os.path.join(sys.path[0], "smiley.gif"),
            os.path.join(sys.path[0], "smiley.ico"), 'Trayicon demo', command=cmd)
    icon.menu.add_command(label='Show info', command=info)
    icon.menu.add_separator()
    icon.menu.add_command(label='Quit', command=root.quit)

    root.mainloop()
    # on windows it seems like tray icons should be explicitely deleted:
    icon.destroy_all()
    root.destroy()
    #raw_input('Demo finished, press "Enter" to exit.')

if __name__ == '__main__':
    test()

