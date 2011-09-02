'''
Created on 18.8.2011

@author: plavc
'''

from gladeui.base import BaseWidget
from scanner.model import Host, Profile
from gladeui.table import PortsWorkbench
import gobject

try:  
    import gtk
except:  
    print("GTK Not Availible")
    
class ScannerPage(BaseWidget):

    def __init__(self, storage, widget=None, label=None):
        super(ScannerPage, self).__init__(widget)
        
        self.label = label
        
        self.storage = storage
        self.signals = { 
            'on_btn_scan_clicked'               : self.on_btn_scan_clicked,
            'on_chk_single_port_toggled'        : self.on_chk_single_port_toggled,
            'on_chk_all_port_toggled'           : self.on_chk_all_port_toggled,
            'on_hostname_input_changed'         : self.on_hostname_input_changed,
            'on_port_start_input_value_changed' : self.on_port_start_input_value_changed,
            'on_port_end_input_value_changed'   : self.on_port_end_input_value_changed,
            'on_btn_load_profile_clicked'       : self.on_btn_load_profile_clicked,
            'on_btn_save_profile_clicked'       : self.on_btn_save_profile_clicked
        }
        
        self.builder.connect_signals(self.signals)
        self.init()

    def init(self):
        self.page_id = -1
        
        self.workbench = PortsWorkbench()
        self.widget.pack_start(self.workbench.get_widget())
        
        hostname_input = self.get_input_object("hostname")
        combo_profile = self.get_input_object("c_profile")
        
        self.he = HostnameEntryHelper(hostname_input)
        self.he.createEntryCompletition()
        self.he.add_hosts(self.storage.get_hosts())
        
        self.ph = ProfileHelper(combo_profile)
        self.ph.create_combo_box()
        self.ph.add_profiles(self.storage.get_profiles())
        
    def on_btn_load_profile_clicked(self, widget):
        combo_profile = self.get_input_object("c_profile")
        hostname_input = self.get_input_object("hostname")
        
        if len(hostname_input.get_text()) == 0:
            return;
        
        iter = combo_profile.get_active_iter()
        
        if iter == None:
            return
        
        model = combo_profile.get_model()
        
        profile = model.get_value(iter, 1)
        
        host = Host(hostname_input.get_text())
        
        self.workbench.clear()
        
        for port in profile.get_ports():
            self.workbench.fill_single_port(host, port)
            
        self.workbench.refresh_ports()

    def on_btn_save_profile_clicked(self, widget):
        combo_profile = self.get_input_object("c_profile")
        
        title = None
        
        if len(combo_profile.get_active_text()) > 0:
            title = combo_profile.get_active_text()
        else:
            return
        
        for p in self.storage.get_profiles():
            if p.get_title() == title:
                return
            
        ports = self.workbench.get_port_list().get_port_list_keys()
        profile = Profile(title, ports)
        
        self.storage.add_profile(profile)
        self.storage.save()
        self.ph.add_profiles([profile,])
        
    def on_btn_scan_clicked(self, widgtet):
        hostname_input = self.get_input_object("hostname")
        chk_single_port = self.get_input_object("single_port")
        port_start = self.get_input_object("port_start")
        port_end = self.get_input_object("port_end")

        host = Host(hostname_input.get_text())
        
        if chk_single_port.get_active():
            self.workbench.fill_single_port(host, port_start.get_value_as_int())
            self.workbench.refresh_ports()
        else:
            self.workbench.fill_port_range(host, port_start.get_value_as_int(), port_end.get_value_as_int())

        self.workbench.refresh_ports()
        self.storage.add_host(host)
        self.storage.save()
        self.he.add_hosts([host,])

    def on_chk_single_port_toggled(self, widgtet):
        chk_single_port = self.get_input_object("single_port")
        chk_all_port = self.get_input_object("all_port")
        
        if chk_single_port.get_active():
            chk_all_port.set_active(False)
        else:
            chk_all_port.set_active(True)
        self.define_port_range()
    
    def on_chk_all_port_toggled(self, widgtet):
        chk_single_port = self.get_input_object("single_port")
        chk_all_port = self.get_input_object("all_port")
        
        if chk_all_port.get_active():
            chk_single_port.set_active(False)
        else:
            chk_single_port.set_active(True)
            
        self.define_port_range()
    
    def define_port_range(self):
        chk_single_port = self.get_input_object("single_port")
        chk_all_port = self.get_input_object("all_port")
        port_end = self.get_input_object("port_end")
        
        if chk_single_port.get_active():
            port_end.set_sensitive(False)
            adj = port_end.get_adjustment()
            adj.set_lower(65535)
            port_end.update()

        if chk_all_port.get_active():
            port_end.set_sensitive(True)
    
    def on_hostname_input_changed(self, widgtet):
        hostname_input = self.get_input_object("hostname")
        
        host = hostname_input.get_text()
        
        if len(host) == 0 :
            self.update_hostname_input(hostname_input, 0)
            return
        
        if len(host) < 5 :
            self.update_hostname_input(hostname_input, -1)
            return
        
        host_parts = host.split(".")
        
        for part in host_parts:
            if not part.isalnum():
                self.update_hostname_input(hostname_input, -1)
                return
            
        self.update_hostname_input(hostname_input, 1)
        self.label.set_text(host)
    
    def update_hostname_input(self, entry, valid):
        btn_scan = self.get_input_object("scan")
        btn_p_load = self.get_input_object("btn_p_load")
        
        if valid == 1:
            entry.set_icon_from_stock(0, "gtk-dialog-info")
            btn_scan.set_sensitive(True)
            btn_p_load.set_sensitive(True)
        elif valid == -1:
            entry.set_icon_from_stock(0, "gtk-dialog-error")
            btn_scan.set_sensitive(False)
            btn_p_load.set_sensitive(False)
        elif valid == 0:
            entry.set_icon_from_stock(0, "gtk-connect")
            btn_scan.set_sensitive(False)
            btn_p_load.set_sensitive(False)
    
    def on_port_start_input_value_changed(self, widgtet):
        port_end_input = self.get_input_object("port_end")
        port_start_input = self.get_input_object("port_start")
        
        adj = port_end_input.get_adjustment()
        adj.set_lower(port_start_input.get_value_as_int())
        port_end_input.update()
    
    def on_port_end_input_value_changed(self, widget):
        port_end_input = self.get_input_object("port_end")
        port_start_input = self.get_input_object("port_start")
        
        adj = port_start_input.get_adjustment()
        adj.set_upper(port_end_input.get_value_as_int())
        port_start_input.update()    

    def set_page_id(self, id):
        self.page_id = id;
        
    def get_page_id(self, id):
        return self.page_id

    def set_label(self, label):
        self.label = label

    def get_status_notebook(self):
        return self.get_input_object("noteST")

    base = {
        'glade_file': 'gui/port_scanner_page_gtk.glade',       
        'widget'    : 'body',
    }
    
    input = {
        'single_port'   : 'chk_single_port',
        'all_port'      : 'chk_all_port',
        'scan'          : 'btn_scan',
        'hostname'      : 'hostname_input',
        'port_start'    : 'port_start_input',
        'port_end'      : 'port_end_input',
        'c_profile'     : 'combo_profile',
        'btn_p_load'    : 'btn_load_profile',
        'btn_p_save'    : 'btn_save_profile'
    }
    
class ScannerPageLabel(BaseWidget):

    def __init__(self, title, notebook = None):
        super(ScannerPageLabel, self).__init__()
        self.get_input_object('title').set_text(title)
        
        self.page_id = -1
        self.notebook = notebook
        
        self.signals = { 
            'on_buttonClose_clicked'  : self.on_button_close_clicked,
        }
        
        self.builder.connect_signals(self.signals)

    def on_button_close_default(self, widget):
        pass

    def set_page_id(self, id):
        self.page_id = id;
    
    def set_text(self, text):
        self.get_input_object('title').set_text('[' + text + ']')
    
    def on_button_close_clicked(self, widget):
        if (self.notebook != None) & (self.page_id > -1):
            self.notebook.remove_page(self.page_id)
        else:
            print "Page id or notebook not defined"
        
    base = {
        'glade_file': 'gui/port_scanner_page_label_gtk.glade',       
        'widget'    : 'labelPage',
    }
    
    input = {
        'title'     : 'title',
        'close'     : 'buttonClose'
    }
    
class HostnameEntryHelper(object):
    
    def __init__(self, text_entry):
        self.text_entry = text_entry
         
    def createEntryCompletition(self):
        self.completion = gtk.EntryCompletion()
        self.text_entry.set_completion(self.completion)
        self.liststore = gtk.ListStore(gobject.TYPE_STRING, gtk.gdk.Pixbuf)
        self.completion.set_model(self.liststore)
        pixbufcell = gtk.CellRendererPixbuf()
        self.completion.pack_start(pixbufcell)
        self.completion.add_attribute(pixbufcell, 'pixbuf', 1)
  
        self.completion.set_text_column(0)
        self.completion.set_popup_set_width(False)
        self.completion.set_match_func(self.match_func, None)
        
    def match_func(self, completion, key, iter, column):
        model = completion.get_model()
        text = model.get_value(iter, 0)
        if text != None and (text.startswith(key) or len(key) == 0):
            return True
        return False
    
    def add_hosts(self, hosts):
        for host in hosts:
            self.liststore.append([host.get_hostname(), self.text_entry.render_icon("gtk-edit",gtk.ICON_SIZE_MENU)])
        
class ProfileHelper(object):
    
    def __init__(self, combo_box):
        self.combo_box = combo_box
        self.store = None
        
    def create_combo_box(self):
        self.store = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)
        self.combo_box.set_model( self.store)
        
    def clear(self):
        self.store.clear()

    def add_profiles(self, profiles):
        for profile in profiles:
            self.store.append([profile.get_title(), profile])
        
    