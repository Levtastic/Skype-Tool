import Tkinter as tk
import ttk
import tkFont
import tkMessageBox
import Skype4Py.enums as sk
import Skype4Py

# http://stackoverflow.com/questions/13029563/skype4py-attach-function-is-not-working-second-time

# each class adds an "AttachmentStatus" event, which if is a success, populates their various lists and such - otherwise, those don't immediately populate

# main class has an attach event which if attach is available, attaches

class AutoAnswer():
    tab_label = 'Auto Answer'
    
    def __init__(self, settings, tab, skype, app_name):
        self.normal_contacts = []
        self.answer_contacts = []
        self.app_name = app_name
        self.skype = skype
        self.settings = settings
        
        fLeft = ttk.Frame(tab)
        fLeft.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)
        
        fTopLeft = ttk.Frame(fLeft)
        fTopLeft.pack(side = tk.TOP, fill = tk.X)
        
        bOn = tk.Button(fTopLeft, text = 'On', relief = (settings.get('auto_answer:is_on', True) and tk.SUNKEN or tk.RAISED))
        bOn.pack(side = tk.LEFT)
        bOff = tk.Button(fTopLeft, text = 'Off', relief = (settings.get('auto_answer:is_on', True) and tk.RAISED or tk.SUNKEN))
        bOff.pack(side = tk.LEFT)
        
        bOn.configure(command = lambda: self._on_off(bOn, bOff, bOn))
        bOff.configure(command = lambda: self._on_off(bOn, bOff, bOff))
        
        fBottomLeft = ttk.Frame(fLeft)
        fBottomLeft.pack(side = tk.BOTTOM, fill = tk.BOTH, expand = True)
        
        l = ttk.Label(fBottomLeft, text = 'Contacts')
        l.pack(side = tk.TOP)
        
        sb = ttk.Scrollbar(fBottomLeft, orient = tk.VERTICAL)
        lNormalContacts = tk.Listbox(fBottomLeft, selectmode = tk.EXTENDED, yscrollcommand = sb.set)
        sb.config(command = lNormalContacts.yview)
        sb.pack(side = tk.RIGHT, fill = tk.Y)
        lNormalContacts.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)
        
        fMiddle = ttk.Frame(tab)
        fMiddle.pack(side = tk.LEFT, fill = tk.BOTH, pady = 100)
        
        bFont = tkFont.Font(size = 18, weight = 'bold')
        bAdd = tk.Button(fMiddle, text = '>', font = bFont, command = lambda: self._swap(True, lNormalContacts, lAnswerContacts))
        bAdd.pack(fill = tk.X)
        bRemove = tk.Button(fMiddle, text = '<', font = bFont, command = lambda: self._swap(False, lNormalContacts, lAnswerContacts))
        bRemove.pack(fill = tk.X)
        
        fRight = ttk.Frame(tab)
        fRight.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)
        
        fTopRight = ttk.Frame(fRight)
        fTopRight.pack(side = tk.TOP, fill = tk.X)
        
        options = [
            'Answer if not in a call',
            'End open calls when answering',
            'Hold open calls when answering',
        ]
        
        cbOptions = ttk.Combobox(fTopRight, values = options, state = 'readonly')
        cbOptions.pack(side = tk.TOP, fill = tk.X, expand = True)
        cbOptions.set(options[self.settings.get('auto_answer:current_setting', 0)])
        cbOptions.bind('<<ComboboxSelected>>', lambda event: self._settings_changed(cbOptions, options))
        
        fBottomRight = ttk.Frame(fRight)
        fBottomRight.pack(side = tk.BOTTOM, fill = tk.BOTH, expand = True)
        
        l = ttk.Label(fBottomRight, text = 'Auto Answer Contacts')
        l.pack(side = tk.TOP)
        
        sb = ttk.Scrollbar(fBottomRight, orient = tk.VERTICAL)
        lAnswerContacts = tk.Listbox(fBottomRight, selectmode = tk.EXTENDED, yscrollcommand = sb.set)
        sb.config(command = lAnswerContacts.yview)
        sb.pack(side = tk.RIGHT, fill = tk.Y)
        lAnswerContacts.pack(side = tk.RIGHT, fill = tk.BOTH, expand = True)
        
        skype.RegisterEventHandler('AttachmentStatus', lambda status: self._on_attachment_status(status, skype, lNormalContacts, lAnswerContacts))
        skype.RegisterEventHandler('CallStatus', self._on_call_status)
    
    def _on_off(self, bOn, bOff, clicked):
        if clicked.config('relief')[-1] == tk.RAISED:
            for button in (bOn, bOff):
                new_relief = button.config('relief')[-1] == tk.SUNKEN and tk.RAISED or tk.SUNKEN
                button.config(relief = new_relief)
        
        self.settings['auto_answer:is_on'] = (bOn is clicked)
    
    def _settings_changed(self, cbOptions, options):
        self.settings['auto_answer:current_setting'] = options.index(cbOptions.get())
    
    def _swap(self, adding, lNormalContacts, lAnswerContacts):
        if adding:
            lFrom, lTo = lNormalContacts, lAnswerContacts
            sFrom, sTo = self.normal_contacts, self.answer_contacts
        else:
            lFrom, lTo = lAnswerContacts, lNormalContacts
            sFrom, sTo = self.answer_contacts, self.normal_contacts
        
        from_contacts = [sFrom.pop(int(index)) for index in lFrom.curselection()]
        if not from_contacts:
            tkMessageBox.showwarning(self.app_name, 'No contacts selected')
            return
        
        sTo += from_contacts
        
        self._populate_lists(lNormalContacts, lAnswerContacts)
    
    def _populate_lists(self, lNormalContacts, lAnswerContacts):
        lNormalContacts.delete(0, 'end')
        lAnswerContacts.delete(0, 'end')
        
        self.normal_contacts.sort(key = lambda contact: contact.Handle)
        self.answer_contacts.sort(key = lambda contact: contact.Handle)
        
        for contact in self.normal_contacts:
            lNormalContacts.insert('end', '%s (%s)' % (contact.FullName, contact.Handle))
        
        for contact in self.answer_contacts:
            lAnswerContacts.insert('end', '%s (%s)' % (contact.FullName, contact.Handle))
        
        answer_contact_handles = [contact.Handle for contact in self.answer_contacts]
        self.settings['auto_answer:answer_contact_handles'] = answer_contact_handles
    
    def _on_attachment_status(self, status, skype, lNormalContacts, lAnswerContacts):
        if status == Skype4Py.apiAttachSuccess:
            self.answer_contacts = []
            self.normal_contacts = []
            
            answer_contact_handles = self.settings.get('auto_answer:answer_contact_handles', [])
            
            for contact in skype.Friends:
                if contact.Handle in answer_contact_handles:
                    self.answer_contacts.append(contact)
                else:
                    self.normal_contacts.append(contact)
            
            self._populate_lists(lNormalContacts, lAnswerContacts)
    
    def _on_call_status(self, call, status):
        if status != sk.clsRinging or call.Type not in (sk.cltIncomingP2P, sk.cltIncomingPSTN):
            return
        
        if not self.settings.get('auto_answer:is_on', True):
            return
        
        if len(call.Participants) > 1:
            handles = self.settings['auto_answer:answer_contact_handles'] + self.skype.CurrentUser.Handle
            for participant in call.Participants:
                if participant.Handle not in handles:
                    return
        
        elif call.PartnerHandle not in self.settings['auto_answer:answer_contact_handles']:
                return
        
        for current_call in self.skype.ActiveCalls:
            if current_call.Status == sk.clsInProgress:
                current_setting = self.settings.get('auto_answer:current_setting', 0)
                
                if current_setting == 0:
                    return
                
                if current_setting == 1:
                    current_call.Finish()
                
                if current_setting == 2:
                    current_call.Hold()
        
        call.Answer()
