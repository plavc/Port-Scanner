'''
Created on 23.8.2011

@author: plavc
'''
from xml.dom.minidom import parse, Document
from locale import atoi

mapping = {
    'root'          : 'scanner',
    'root_profiles' : 'profiles',
    'profile'       : 'profile',
    'profile_title' : 'title',
    'profile_ports' : 'ports',
    'profile_port'  : 'port',
    
    'root_cmpt'     : 'completition',
    'host'          : 'host'
    
    }
(
    PORT_CLOSED,
    PORT_OPENED,
    PORT_PENDING,
    PORT_OPENED_TCP,
    PORT_OPENED_UDP
) = range(5)

class Port(object):
    '''
    Port class, holding scanning port data, port number, open/closed,
    host object with  host name and date of execution and duration
    '''
    def __init__(self, port_number=0, open=False, host=None):
        self.port_number = port_number
        self.host = host
        self.date = None
        self.duration = 0
        self.status = PORT_PENDING
        
    def get_port_number(self):
        return self.port_number
    
    def set_port_number(self, port_number):
        self.port_number = port_number
    
    def get_status(self):
        return self.status
    
    def set_status(self, status):
        self.status = status
        
    def get_host(self):
        return self.host
    
    def set_host(self, host):
        self.host = host
    
    def get_date(self):
        return self.date
    
    def set_date(self, date):
        self.date = date
        
    def get_duration(self):
        return self.duration
    
    def set_duration(self, duration):
        self.duration = duration
              
class Host(object):
    '''
    Host class holds data for host name for Port object
    '''
    def __init__(self, hostname=None):
        self.hostname = hostname
        
    def clone(self):
        return Host(self.get_hostname())
        
    def get_hostname(self):
        return self.hostname
    
    def set_hostname(self, hostname):
        self.hostname = hostname

class PortList(object):
    '''
    Class holding list of ports. Port numbers
    cannot be duplicated
    '''
    def __init__(self):
        self.port_list = {}
        
    def add_port(self, port):
        if self.port_list.has_key(port.get_port_number()):
            return False
        else:
            self.port_list[port.get_port_number()] = port;
            return True
            
    def remove_port(self, port_number):
        if self.port_list.has_key(port_number):
            del self.port_list[port_number]
            return True
        else:
            return False     
    
    def get_port_list_values(self):
        return self.port_list.values()
    
    def get_port_list_keys(self):
        return self.port_list.keys()
    
    def clear(self):
        self.port_list.clear()

class Profile(object):
    
    def __init__(self, title=None, ports=None):
        self.title = title
        if ports != None:
            self.ports = set(ports)
        else:
            self.ports = set()
        
    def add_port(self, port):
        self.ports.add(port)
        
    def remove_port(self, port):
        self.ports.remove(port)
        
    def clear(self):
        self.ports.clear()
        
    def get_ports(self):
        return self.ports
    
    def get_title(self):
        return self.title
    
    def set_title(self, title):
        self.title = title
    
class Storage():
    
    def __init__(self, filename="settings.xml"):
        self.profiles = []
        self.hosts = []
        self.filename = filename
    
    def save(self):
        try:
            self.serialize()
        except Exception as ex:
            print "Could not save data. An error occurred."
            print ex
            return False
        
        return True
        
    def read(self):
        try:
            self.deserialize()
        except Exception as ex:
            print "Could not retrieve saved data!"
            print ex
            return False
        
        return True
   
    def serialize(self):
        self.document = Document()
        
        root = self.document.createElement(mapping['root'])
        self.document.appendChild(root)
        
        root_profiles = self.document.createElement(mapping['root_profiles'])
        root.appendChild(root_profiles)
        
        # serialize profiles
        self.serialize_profiles(root_profiles, self.profiles)
        
        root_hosts = self.document.createElement(mapping['root_cmpt'])
        root.appendChild(root_hosts)
        
        self.serialize_hostnames(root_hosts, self.hosts)
        
        try:
            xmlFile = open(self.filename, "w")
            self.document.writexml(xmlFile)
        except Exception as ex:
            print("Could not save file")
            print ex
            return False
        
        return True
    
    def serialize_profiles(self, root, profiles):
        for profile in profiles:
            entry = self.document.createElement(mapping['profile'])
            
            title_node = self.document.createElement(mapping['profile_title'])
            text = self.document.createTextNode(profile.get_title())
            title_node.appendChild(text)
            entry.appendChild(title_node)
        
            ports_node = self.document.createElement(mapping['profile_ports'])
            
            for port in profile.get_ports():
                port_node = self.document.createElement(mapping['profile_port'])
                text = self.document.createTextNode(str(port))
                port_node.appendChild(text)
                ports_node.appendChild(port_node)
                
            entry.appendChild(ports_node)
            root.appendChild(entry)
            
    def serialize_hostnames(self, root, hosts):
        for host in hosts:
            entry = self.document.createElement(mapping['host'])
            text = self.document.createTextNode(host.get_hostname())
            entry.appendChild(text)
            root.appendChild(entry) 
              
    def deserialize(self):
        document = parse(self.filename)
        
        self.deserialize_profiles(document)
        self.deserialize_hosts(document)
    
    def deserialize_profiles(self, document):
        self.profiles = []
        root_profiles = document.getElementsByTagName(mapping['root_profiles'])[0]
    
        entries = root_profiles.getElementsByTagName(mapping['profile'])
                
        for entry in entries:
            obj = Profile()
    
            title_node = entry.getElementsByTagName(mapping['profile_title'])[0]
            ports_node = entry.getElementsByTagName(mapping['profile_ports'])[0]
            
            obj.set_title(title_node.childNodes[0].data)
        
            port_entries = ports_node.getElementsByTagName(mapping['profile_port'])
            
            for p_entry in port_entries:
                port = p_entry.childNodes[0].data
                obj.add_port(atoi(port))

            self.profiles.append(obj)
            
        return self.profiles

    def deserialize_hosts(self, document):
        self.hosts = []
        root_profiles = document.getElementsByTagName(mapping['root_cmpt'])[0]
    
        entries = root_profiles.getElementsByTagName(mapping['host'])
                
        for entry in entries:
            obj = Host(entry.childNodes[0].data)
            self.hosts.append(obj)
            
        return self.hosts

    def get_profiles(self):
        if self.profiles == None:
            self.read()
        
        return self.profiles
    
    def add_profile(self, profile):
        self.profiles.append(profile)
        
    def get_hosts(self):
        if self.hosts == None:
            self.read()
            
        return self.hosts
    
    def add_host(self, host):
        for h in self.hosts:
            if h.get_hostname() == host.get_hostname():
                pass
        self.hosts.append(host)
            
if __name__ == '__main__':
    storage = Storage()
    
    storage.add_profile(Profile("Default", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))
    storage.add_profile(Profile("Common", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))
    
    storage.add_host(Host("loclahost"))
    storage.add_host(Host("plavcak.net"))
    
    storage.save()

    