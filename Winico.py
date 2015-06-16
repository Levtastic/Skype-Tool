# -*- coding: utf-8 -*-
import Tkinter

class Icon:
    def __init__(self, filename=None, resourcename=None):
        '''Load icons from a .ico file FILENAME. Icon files often contain several
        icons for different color depths of the screen and may contain
        different sizes (e.g. 16x16 and 32x32 icons).
        If RESOURCENAME is given, load icons from the resource section of
        an executable file FILENAME (.exe or .dll). Only icons for the current colordepth
        are loaded (unlike when loading an .ico file). RESOURCENAME may be a string
        identifier or a number that identifies the item in the resource file.
        If no FILENAME is given then you may load some standard windows icons
        (defined for the LoadIcon Win32 API function). The following names are recognised:
        "application", "asterisk", "error", "exclamation", "hand", "question",
        "information", "warning", and "winlogo".'''
        self.master = Tkinter._default_root
        if not self.master:
            raise RuntimeError, 'Too early to create tray icon.'
        self.WinicoVersion = self.master.tk.call('package', 'require', 'Winico')
        if resourcename:
            self._id = self.master.tk.call('winico', 'load', resourcename, filename)
        else:
            self._id = self.master.tk.call('winico', 'createfrom', filename)

    def delete(self):
        '''Free the resource identified by SELF. This command is always successful,
        even in SELF's id is invalid.'''
        self.master.tk.call('winico', 'delete', self._id)
    destroy = delete

    def delete_all(self):
        '''Convenience fiunction, deletes all current icon ids.'''
        for icon_id in self.info():
            self.master.tk.call('winico', 'delete', icon_id)
    destroy_all = delete_all

    def info(self):
        '''Returns a tuple of all the current icon ids.'''
        return self.master.tk.splitlist(self.master.tk.call('winico', 'info'))

    def info_id(self):
        '''Returns information about icon resources managed by this extension.
        The result is a list of dictionaries of option value pairs for each
        icon in the icon resource.
        For identifiers created via RESOURCENAME the values given are not relevant.
        pos
            position inside the iconresource (beginning from 0)
        width
            width of the icon in pixels
        height
            height of the icon in pixels
        geometry
            widthxheight in pixels (for convenience)
        bpp
            color depth in bits per pixel (4 means 16 colors)
        hicon
            windows icon handle for this icon (in the actual version all hicons of a resource will be immediately created after reading from disk, in later versions this may occur on demand , to economize system load )
        ptr
            C-pointer of the internal struct, only interesting for hackers :-) '''
        # returns a list of dictionaries
        # the original tcl output looks like:
        # {-pos 0 -width 32 -height 32 -geometry 32x32 -bpp 4 -hicon 0x670081 -ptr 0xf99884} {-pos 1 -width 16 -height 16 -geometry 16x16 -bpp 4 -hicon 0xad01b4 -ptr 0xf99884}
        res = self.master.tk.split(self.master.tk.call('winico', 'info', self._id))
        info = []
        for x in res:
            # res is a tuple of tuples
            x = [a for a in x]
            cnf = {}
            while x:
                cnf[x[0][1:]] = x[1]
                x = x[2:]
            info.append(cnf)
        return info

    def register(self, *args, **kw):
        return self.master.register(*args, **kw)

    def setwindow(self, windowid, size='big', pos=None):
        '''Set the icon for the toplevel window given by windowid which may be either
        the Tk pathname for the window, or a valid Windows HWND value (for use with non-Tk windows).
        NOTE: the window MUST BE MAPPED. If not then this may fail or crash.
        size
            If size is "big" (default) the taskbar icon AND the caption icon are set under Win95/WinNT,
            if it's "small" only the small caption icon is set (via WM_SETICON).
            Under Win32s size is ignored (setting done via SetClassLong()) (for setting individual
            toplevels different Windows-classnames per toplevel would be required , TkToplevel0,
            TkToplevel1 and so on)
        pos
            If pos is set, the icon with that -pos number is used for setting the toplevel icon,
            otherwise winico chooses the first 32x32 16color icon (this could be improved)
            This option only has an effect on icons created with the "createfrom" subcommand
            (FIX ME: check this)'''
        return self.tk.call('winico', 'setwindow', windowid, self._id, size, pos)

    def taskbar_add(self, text=None, pos=None, callback=None):
        '''Add an icon registration to the Windows taskbar.
        You should probably also provide a -text argument otherwise the icon id will be used
        for the text too (Windows displays the text as a tooltip).
        The optional callback is for specifying a Tcl procedure to be called when events
        occur on the icon. This includes mouse motion and button click events. In the
        callback there are bind-like abbreviations possible :
        %m      the windows message specifier, may be one of:
                WM_MOUSEMOVE, WM_LBUTTONDOWN, WM_LBUTTONUP, WM_LBUTTONDBLCLK,
                WM_RBUTTONDOWN, WM_RBUTTONUP, WM_RBUTTONDBLCLK, WM_MBUTTONDOWN,
                WM_MBUTTONUP, WM_MBUTTONDBLCLK
        %i      the icon identifier (ico#1, ico#2 a.s.o)
        %x      current xposition of the cursor
        %y      current yposition of the cursor
        %X      xposition of the cursor when the last windows-message was processed
        %Y      yposition of the cursor when the last windows-message was processed
                (%X,%Y may differ from %x,%y however the difference is marginal )
        %t      current tickcount of the system
        %w      wParam of the internal callback message (the integer part of %i)
        %l      lParam of the internal callback message (integer value of %m)
        %%      a %-sign

        Usage example of the callback option:
            ico = Icon("some.ico")
            def func(eventtype, x, y):
                if eventtype == "WM_RBUTTONDOWN":
                    show_context_menu(x, y)
            callback = ico.register(func)
            ico.taskbar_add(text="hi!", callback=(callback, '%m', '%x', '%y')) '''
        args = ()
        if callback:
            args += ('-callback', callback)
        if pos:
            args += ('-pos', pos)
        if text:
            args += ('-text', text)
        return self.master.tk.call('winico', 'taskbar', 'add', self._id, *args)

    def taskbar_delete(self):
        '''Remove this icon from the status area.'''
        return self.master.tk.call('winico', 'taskbar', 'delete', self._id)

    def taskbar_modify(self, text=None, pos=None, callback=None):
        '''Modify an icon registration with the Windows taskbar.
        To modify the command, text or the icon displayed in the taskbar status area, use
        the callback, pos and text options to change the current settings. '''
        args = ()
        if callback:
            args += ('-callback', callback)
        if pos:
            args += ('-pos', pos)
        if text:
            args += ('-text', text)
        return self.master.tk.call('winico', 'taskbar', 'modify', self._id, *args)


########################################################################
def test():

    root = Tkinter.Tk()
    #root.withdraw()
    ico = Icon("C:/Python26/tcl/winico0.6/smiley.ico")
    ico.taskbar_add(pos=0, text="foo")
    ico2 = Icon(None, "asterisk")
    ico2.taskbar_add(pos=2, text='foo')
    print ico.info_id()
    print ico.info()

    def func(eventtype, x, y):
        if eventtype == "WM_RBUTTONDOWN":
            print 'foobar', x, y

    f = root.register(func)
    ico.taskbar_modify(text='bla', callback=(f, '%m', '%x', '%y'))
    #print
    #print ico2.info()
    #print 'c', ico.taskbar_delete()
    root.mainloop()

    ico.destroy_all()
    raw_input()

if __name__ == '__main__':
    test()

