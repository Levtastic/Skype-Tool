import Tkinter as tk
import ttk
import tkMessageBox
import Skype4Py

class MassSender():
    tab_label = 'Send Message'
    
    def __init__(self, settings, tab, skype, app_name):
        self.contacts = []
        self.app_name = app_name
        self.skype = skype
        
        fTop = ttk.Frame(tab)
        fTop.pack(side = tk.TOP)
        
        fMain = ttk.Frame(tab)
        fMain.pack(fill = tk.BOTH, expand = True)
        
        sb = ttk.Scrollbar(fMain, orient = tk.VERTICAL)
        lContacts = tk.Listbox(fMain, selectmode = tk.EXTENDED, yscrollcommand = sb.set)
        sb.config(command = lContacts.yview)
        sb.pack(side = tk.RIGHT, fill = tk.Y)
        lContacts.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)
        
        l = ttk.Label(fTop, text = 'Select')
        l.pack(side = tk.LEFT)
        
        bAll = tk.Button(fTop, text = 'All', command = lambda: lContacts.selection_set(0, 'end'))
        bAll.pack(side = tk.LEFT)
        
        l = ttk.Label(fTop, text = '/')
        l.pack(side = tk.LEFT)
        
        bNone = tk.Button(fTop, text = 'None', command = lambda: lContacts.selection_clear(0, 'end'))
        bNone.pack(side = tk.LEFT)
        
        fBottom = ttk.Frame(tab)
        fBottom.pack(side = tk.BOTTOM, fill = tk.BOTH, expand = True)
        
        tMessage = tk.Text(fBottom, width = 50, height = 6, wrap = tk.WORD)
        tMessage.pack(side = tk.TOP, fill = tk.BOTH, expand = True)
        
        bSend = ttk.Button(fBottom, text = 'Send', command = lambda: self._send(lContacts, tMessage))
        bSend.pack(side = tk.BOTTOM)
        
        skype.RegisterEventHandler('AttachmentStatus', lambda status: self._on_attachment_status(status, lContacts))
    
    def _on_attachment_status(self, status, lContacts):
        if status == Skype4Py.apiAttachSuccess:
            self._populate(lContacts)
    
    def _populate(self, lContacts):
        self.contacts = []
        lContacts.delete(0, 'end')
        
        for contact in self.skype.Friends:
            self.contacts.append(contact)
        
        self.contacts.sort(key = lambda contact: contact.Handle)
        
        for contact in self.contacts:
            lContacts.insert('end', '%s (%s)' % (contact.FullName, contact.Handle))
    
    def _send(self, lContacts, tMessage):
        message = tMessage.get('1.0', 'end-1c').strip()
        if not message:
            tkMessageBox.showwarning(self.app_name, 'No message entered')
            return
        
        selected_contacts = [self.contacts[int(selected_index)] for selected_index in lContacts.curselection()]
        if not selected_contacts:
            tkMessageBox.showwarning(self.app_name, 'No contacts selected')
            return
        
        if not tkMessageBox.askyesno(self.app_name, 'Send message to selected people?'):
            return
        
        failed, succeeded = 0, 0
        for contact in selected_contacts:
            try:
                self.skype.SendMessage(contact.Handle, message)
                succeeded += 1
            except:
                failed += 1
        
        if failed:
            tkMessageBox.showinfo(self.app_name, 'Message sent to %d contacts (%d failed)' % (succeeded, failed))
        else:
            tkMessageBox.showinfo(self.app_name, 'Message sent to %d contacts' % succeeded)
