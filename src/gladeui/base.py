'''
Created on 7.7.2011

@author: plavc
'''
  
try:  
    import gtk
except:  
    print("GTK Not Available")

DIALOG_RESULT_OK = 1
DIALOG_RESULT_CANCEL = -1

class BaseWidget(object):

    def __init__(self, widget=None):
        self.builder = gtk.Builder()
        self.builder.add_from_file(self.base['glade_file'])
        if widget == None:
            self.widget = self.get_base_object('widget')
    
    def get_input_object(self, name):
        return self.builder.get_object(self.input[name])
        
    def get_base_object(self, name):
        return self.builder.get_object(self.base[name])
        
    def get_builder(self):
        if self.builder == None:
            self.builder = gtk.Builder()
            
        return self.builder
    
    def get_widget(self):
        return self.widget
    
    base = {
        'glade_file'    : None,       
        'widget'        : None,
    }
    
    input = { }  
    