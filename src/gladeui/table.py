'''
Created on 19.8.2011

@author: plavc
'''

import gobject
from gladeui.base import BaseWidget
from scanner.model import PortList, Port
import subprocess
import time
from multiprocessing.process import Process
from scanner import model

try:  
    import gtk
except:  
    print("GTK Not Availible")
    
(
    P_COLUMN_FIRST,
    P_COLUMN_HOST,
    P_COLUMN_NUMBER,
    P_COLUMN_DURATION,
    P_COLUMN_DESCRIPTION
) = range(5)

MAX_POOL_SIZE = 10

class PortsWorkbench(BaseWidget):
    
    def __init__(self):
        super(PortsWorkbench, self).__init__()

        self.signals = {             
            'on_btn_ports_all_clicked'     : self.on_btn_ports_all_clicked,
            'on_btn_ports_open_toggled'    : self.on_btn_ports_open_toggled,
            'on_btn_ports_closed_toggled'  : self.on_btn_ports_closed_toggled,
            'on_btn_ports_to_scan_toggled' : self.on_btn_ports_to_scan_toggled,
            'on_btn_ports_start_clicked'   : self.on_btn_ports_start_clicked,
            'on_btn_ports_remove_clicked'  : self.on_btn_ports_remove_clicked,
            'on_btn_ports_remove_all_clicked'   : self.on_btn_ports_remove_all_clicked,
            'on_btn_ports_start_all_clicked'    : self.on_btn_ports_start_all_clicked,
            'on_btn_ports_refresh_clicked'      : self.on_btn_ports_refresh_clicked,
        }
        
        self.pool_size = MAX_POOL_SIZE
        self.quie = []
        
        self.builder.connect_signals(self.signals)
        
        self.p_table = self.get_input_object('p_table')
        
        self.portsTable = PortsTable(self.p_table)
        
        self.port_list = PortList()

    def fill_port_range(self, host, start, end):
        for i in range(start, end + 1):
            self.port_list.add_port(Port(i, False, host))
    
    def fill_single_port(self, host, port):
        self.port_list.add_port(Port(port, False, host))
        
    def refresh_ports(self):
        self.portsTable.clear()
        for port in self.port_list.get_port_list_values():
            self.portsTable.add_row(port)

    def on_btn_ports_refresh_clicked(self, widget):
        self.refresh_ports()
 
    def on_btn_ports_all_clicked(self, widget):
        self.get_input_object('p_open').set_active(True)
        self.get_input_object('p_closed').set_active(True)
        self.get_input_object('p_to_scan').set_active(True)

    def on_btn_ports_open_toggled(self, widget):
        self.portsTable.set_view_property(model.PORT_OPENED,self.get_input_object('p_open').get_active())
        self.refresh_ports()
        
    def on_btn_ports_closed_toggled(self, widget):
        self.portsTable.set_view_property(model.PORT_CLOSED ,self.get_input_object('p_closed').get_active())
        self.refresh_ports()
        
    def on_btn_ports_to_scan_toggled(self, widget):
        self.portsTable.set_view_property(model.PORT_PENDING,self.get_input_object('p_to_scan').get_active())
        self.refresh_ports()
        
    def on_btn_ports_start_clicked(self, widget):
        p_table = self.get_input_object('p_table')
        (model, iter) = p_table.get_selection().get_selected()
        
        if iter == None: return
        
        port = model.get_value(iter, 0)
        
        if port != None:
            if self.pool_size == 0:
                self.quie.append(port)
            else:
                self.pool_size -= 1
                Process(group=None,target=self.func,name=None, args=(port,), kwargs={}).run()
    
    def func(self, port):
        start_time = time.time()
        status = subprocess.call(["nc", "-zv", port.get_host().get_hostname(), str(port.get_port_number())])
        port.set_duration(time.time() - start_time)

        if status == 0:
            port.set_status(model.PORT_OPENED)
        elif status > 0:
            port.set_status(model.PORT_CLOSED)

        self.pool_size += 1
        self.check_quie()
        
    def check_quie(self):
        if self.pool_size < MAX_POOL_SIZE:
            Process(group=None,target=self.func,name=None, args=(self.quie.pop(),), kwargs={}).run()
            self.pool_size += 1
        
    def on_btn_ports_start_all_clicked(self, widget):
        gtk.threads_enter()
        for port in self.port_list.get_port_list_values():
            self.scan_all(port)
        gtk.threads_leave()
            
    def scan_all(self, port):
        if self.pool_size == 0:
            self.quie.append(port)
        else:
            self.pool_size -= 1
            Process(group=None,target=self.func,name=None, args=(port,), kwargs={}).run()
    
    def on_btn_ports_remove_clicked(self, widget):
        p_table = self.get_input_object('p_table')
        
        (model, iter) = p_table.get_selection().get_selected()
        
        if iter == None:
            return
        
        iter = model.convert_iter_to_child_iter(iter)
        
        port = model.get_model().get_value(iter, 0)
        self.port_list.remove_port(port.get_port_number())
        
        model.get_model().remove(iter)
    
    def on_btn_ports_remove_all_clicked(self, widget):
        self.portsTable.clear()
        self.port_list.clear()
        
    def get_port_list(self):
        return self.port_list
    
    def clear(self):
        self.port_list.clear()
    
    base = {
        'glade_file': 'gui/port_scanner_page_ports_table_gtk.glade',       
        'widget'    : 'mainBox',
    }
    
    input = {
        'p_all'         : 'btn_ports_all',
        'p_open'        : 'btn_ports_open',
        'p_closed'      : 'btn_ports_closed',
        'p_to_scan'     : 'btn_ports_to_scan',
        'p_start'       : 'btn_ports_start',
        'p_remove'      : 'btn_ports_remove',
        'p_table'       : 'tree_ports_result',
        'p_refresh'     : 'btn_ports_refresh',
    }

class PortsTable(object):
    '''
    Ports Table class containing methods to build data store
    and data view for ports result table
    '''
    def __init__(self, treeview=None):
        
        self.view_filter = {
            model.PORT_CLOSED      : False,
            model.PORT_OPENED      : False,
            model.PORT_PENDING     : True,
        }
        
        self.treeview = treeview
        
        if self.treeview != None:
            self.create_model(self.treeview)
            self.create_view(self.treeview)
    
    def set_view_property(self, property, value):
        if not self.view_filter.has_key(property):
            raise RuntimeError('Property ' + property + 'does not exists')
        else:
            self.view_filter[property] = value
    
    def create_model(self, treeview):
        self.portTableStore = gtk.ListStore(gobject.TYPE_PYOBJECT, gobject.TYPE_STRING, gobject.TYPE_INT, gobject.TYPE_FLOAT, gobject.TYPE_INT)
        treeview.set_model(self.portTableStore)
        
        filter = self.portTableStore.filter_new()
        
        filter.set_visible_func(self.view_filter_function)
        
        treeview.set_model(filter)
        
    def view_filter_function(self, model, iter, user_data=None):
        port = model.get_value(iter, 0)
        
        if port != None:
            return self.view_filter.get(port.get_status(), True)
        else:
            return True
    
    def add_row(self, port):
        iter = self.portTableStore.append()
        self.portTableStore.set(iter, 
                                0, port, 
                                1, port.get_host().get_hostname(), 
                                2, port.get_port_number(),
                                3, port.get_duration(),
                                4, port.get_status())
    
    def create_view(self, treeview):
        # First empty column
        column = gtk.TreeViewColumn()
        column.set_title("#")
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_fixed_width(30)
        
        cell_renderer = gtk.CellRendererPixbuf()
        cell_renderer.set_property('xpad', 2)
        
        column.pack_start(cell_renderer, False)
        column.set_cell_data_func(cell_renderer, self.status_set_func_icon)
        
        treeview.append_column(column)
        
        # Second icon and port number column
        column = gtk.TreeViewColumn()
        column.set_title("Port number")
        column.set_min_width(130)

        cell_renderer = gtk.CellRendererPixbuf()
        cell_renderer.set_property('xpad', 16)
        
        column.pack_start(cell_renderer, False)
        column.set_attributes(cell_renderer, stock_id=1)
        column.set_cell_data_func(cell_renderer, self.port_number_set_func_icon)

        cell_renderer = gtk.CellRendererText()
        cell_renderer.set_property('xalign', 0.1)
        
        column.pack_start(cell_renderer, True)
        column.set_cell_data_func(cell_renderer, self.port_number_set_func_text)
        
        column.set_sort_column_id(2)

        # Hostname column
        cell_renderer = gtk.CellRendererText()
        cell_renderer.set_property('editable', True)
        cell_renderer.connect("edited", self.on_cell_edited, self.portTableStore)
        
        
        treeview.insert_column_with_data_func(P_COLUMN_HOST, "Hostname", cell_renderer, self.hostname_set_func)
        treeview.get_column(P_COLUMN_HOST).set_min_width(200)
        treeview.get_column(P_COLUMN_HOST).set_resizable(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        treeview.get_column(P_COLUMN_HOST).set_sort_column_id(1)
        
        # Adding port number column
        treeview.append_column(column)
        
        # Duration column
        cell_renderer = gtk.CellRendererText()
        cell_renderer.set_property('xalign', 0.4)
        treeview.insert_column_with_data_func(P_COLUMN_DURATION, "Duration", cell_renderer, self.duration_set_func)
        treeview.get_column(P_COLUMN_DURATION).set_sort_column_id(3)
        treeview.get_column(P_COLUMN_DURATION).set_min_width(120)
        
        # Date column
        cell_renderer = gtk.CellRendererText()
        treeview.insert_column_with_data_func(P_COLUMN_DESCRIPTION, "Description", cell_renderer, self.description_set_func)
        treeview.get_column(P_COLUMN_DESCRIPTION).set_sort_column_id(P_COLUMN_DESCRIPTION)
        treeview.get_column(P_COLUMN_DESCRIPTION).set_resizable(gtk.TREE_VIEW_COLUMN_AUTOSIZE)

    def on_cell_edited(self, cell, path_string, new_text, model):
        iter = model.get_iter_from_string(path_string)
            
        port = model.get_value(iter, 0)
        
        host = port.get_host().clone()
        host.set_hostname(new_text)
        port.set_host(host)
        
        port.set_status(model.PORT_PENDING)
        port.set_duration(0)

    def status_set_func_icon(self, tree_column, cell, mod, iter):
        info = mod.get_value(iter, 0)
        if info.get_status() == model.PORT_PENDING:
            cell.set_property("stock_id", "gtk-disconnect")
        else:
            cell.set_property("stock_id", "gtk-disconnect")

    def port_number_set_func_icon(self, tree_column, cell, mod, iter):
        info = mod.get_value(iter, 0)
        if info.get_status() == model.PORT_OPENED:
            cell.set_property("stock_id", "gtk-ok")
        elif info.get_status() == model.PORT_CLOSED:
            cell.set_property("stock_id", "gtk-remove")
        elif info.get_status() == model.PORT_PENDING:
            cell.set_property("stock_id", None)
            
    def port_number_set_func_text(self, tree_column, cell, model, iter):
        info = model.get_value(iter, 0)
        cell.set_property("text", info.get_port_number())

    def hostname_set_func(self, tree_column, cell, model, iter):
        info = model.get_value(iter, 0)
        cell.set_property("text", info.get_host().get_hostname())

    def duration_set_func(self, tree_column, cell, model, iter):
        info = model.get_value(iter, 0)
        duration_s = "{:.2g} s".format(info.get_duration())
        cell.set_property("text", duration_s)

    def description_set_func(self, tree_column, cell, model, iter):
        #info = model.get_value(iter, 0)
        cell.set_property("text", "Port")
  
    def clear(self):
        self.portTableStore.clear()
        
        