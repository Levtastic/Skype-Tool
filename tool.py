import Tkinter as tk, tkMessageBox, ttk, TrayIcon
import os, sys, shelve
import Skype4Py

from mass_sender import MassSender
from auto_answer import AutoAnswer

class Tool():
    def __init__(self):
        self.app_name = app_name = 'Skype Tool'
        
        skype = Skype4Py.Skype()
        skype.RegisterEventHandler('AttachmentStatus', lambda status: self._on_attachment_status(skype, status))
        
        self.settings = settings = shelve.open('settings.dat')
        
        self.root = root = tk.Tk()
        root.protocol('WM_DELETE_WINDOW', self._hide)
        root.bind('<Unmap>', self._on_minimise)
        
        root.title(app_name)
        root.minsize(450, 350)
        
        icon = TrayIcon.Icon(ico = self._resource_path('icon.ico'), tooltip = app_name, command = self._toggle_window)
        icon.menu.add_command(label = 'Show / Hide ' + app_name, command = self._toggle_window)
        icon.menu.add_command(label = 'Reconnect', command = lambda: self._attach(skype))
        icon.menu.add_separator()
        icon.menu.add_command(label = 'Quit', command = root.quit)
        
        tabs = ttk.Notebook(root)
        tabs.pack(fill = tk.BOTH, expand = True)
        
        for TabClass in (MassSender, AutoAnswer):
            tab_frame = ttk.Frame(tabs)
            tabs.add(tab_frame, text = TabClass.tab_label)
            TabClass(settings, tab_frame, skype, app_name)
        
        root.iconbitmap(self._resource_path('icon.ico'))
        root.lift()
        
        root.after(1, self._attach, skype)
        root.mainloop()
        
        settings.close()
        icon.destroy_all()
        root.destroy()
    
    def _on_attachment_status(self, skype, status):
        if status == Skype4Py.apiAttachAvailable:
            self._attach(skype)
    
    def _attach(self, skype):
        self.root.config(cursor = 'wait')
        self.root.update()
        
        try:
            skype.Attach()
        except Skype4Py.errors.SkypeAPIError as e:
			tkMessageBox.showerror(self.app_name, '%s: %s' % (type(e).__name__, str(e)))
        
        self.root.config(cursor = '')
    
    def _resource_path(self, relative):
        if getattr(sys, 'frozen', False):
            basedir = sys._MEIPASS
        else:
            basedir = os.path.dirname(__file__)
        
        return os.path.join(basedir, relative)
    
    def _on_minimise(self, event):
        if event.widget is self.root and self.root.state() != 'withdrawn':
            self._hide()
    
    def _toggle_window(self, x_coord = None, y_coord = None):
        if self.root.state() == 'withdrawn':
            self._show()
        else:
            self._hide()
    
    def _hide(self):
        self.settings.sync()
        self.root.withdraw()
    
    def _show(self):
        self.root.deiconify()

if __name__ == '__main__':
    Tool()
