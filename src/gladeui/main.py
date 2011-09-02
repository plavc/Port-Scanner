'''
Created on 18.8.2011

@author: plavc
'''

from gladeui.base import BaseWidget
from gladeui.page import ScannerPage, ScannerPageLabel
from scanner.model import Storage

try:  
    import gtk
except:  
    print("GTK Not Availible")

class PortScannerWindow(BaseWidget):
    
    def __init__(self): 
        super(PortScannerWindow, self).__init__()
        self.signals = { 
            'gtk_main_quit'                 : gtk.main_quit,
            'on_btn_new_tab_clicked'        : self.on_btn_new_tab_clicked,
            'on_menu_item_about_activate'   : self.on_menu_item_about_activate,
        }
        
        self.builder.connect_signals(self.signals)
        self.init()
        
    def init(self):
        self.storage = Storage()
        self.storage.read()
        self.mainNotebook = self.get_input_object('mainNotebook')
        
    def on_menu_item_about_activate(self, widget):
        aboutDlg = AboutDialog()
        aboutDlg.run()
   
    def on_btn_new_tab_clicked(self, widget):
        page = ScannerPage(self.storage) 
        label = ScannerPageLabel("[new scanner]", self.mainNotebook)
        
        id = self.mainNotebook.append_page(page.get_widget(), label.get_widget())
        
        label.set_page_id(id)
        page.set_page_id(id)
        page.set_label(label)
    
    def get_selected_page(self):
        mainNotebook = self.get_input_object('mainNotebook')
        widget = mainNotebook.get_nth_page(mainNotebook.get_current_page())
        
        page = ScannerPage(widget)
        page.set_page_id(mainNotebook.get_current_page())
        
        return page
    
    def set_notebook_status(self, log, status):
        notebookStatusLog = self.get_selected_page().get_status_notebook()
        
        if log == status:
            notebookStatusLog.hide()
            return
        else:
            notebookStatusLog.show()
        
        if status:
            notebookStatusLog.set_current_page(0)
        elif log:
            notebookStatusLog.set_current_page(1)
            
    def run(self):
        #gtk.gdk.threads_init()
        gtk.main()

    base = {
        'glade_file': 'gui/port_scanner_gtk.glade',       
        'widget'    : 'main_window',
    }
    
    input = {
        'new_tab'       : 'btn_new_tab',
        'log'           : 'btn_log',
        'status'        : 'btn_status',
        'mainNotebook'  : 'mainNotebook'
    }

class AboutDialog(BaseWidget):
    def __init__(self): 
        super(AboutDialog, self).__init__()
        self.signals = { 
            'gtk_main_quit'                 : gtk.main_quit,
        }
        
        self.builder.connect_signals(self.signals)
        self.init()
        
    def init(self):
        pass
    
    def run(self):
        self.widget.run()
    
    base = {
        'glade_file': 'gui/port_scanner_about_gtk.glade',       
        'widget'    : 'aboutdialog',
    }
    
    input = {
    }
    
if __name__ == '__main__':
    psw = PortScannerWindow()
    psw.run()
    
    
        