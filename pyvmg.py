import re
import glob
import datetime

def escapexml(xmldata):
    xmldata = xmldata.replace('&', '&amp;')
    xmldata = xmldata.replace('<', '&lt;')
    xmldata = xmldata.replace('>', '&gt;')
    xmldata = xmldata.replace('"', '&quot;')
    return xmldata

def datecmp(x,y):
    if x['date'] < y['date']:
        return -1
    elif x['date'] == y['date']:
        return 0
    else:
        return 1
    
class VMGReader(object):
    """Reader for a .vmg file to get back the telephone number, date, body
    """
    def __init__(self):
        """Initialize with the required regexes
        """
        self.telre = re.compile(r'TEL:(\+?\d+)')
        self.datere = re.compile(r'X-NOK-DT:([\dTZ]+)')
        self.bodyre = re.compile(r'Date:[\d.: ]+\n(.*)END:VBODY',re.DOTALL)
    
    def read(self, filename):
        """Open a .vmg file and remove the NULL characters and store the text message
        """
        self.filename = filename
        self.message = open(filename, 'r').read()
        self.message = self.message.replace('\0', '')

    def process(self):
        """Parse the message and return back a dictionary with
        telephone number, date and body of message
        """
        data = {}
        telmatch = self.telre.search(self.message)
        if telmatch:
            data['telno'] = telmatch.group(1)
        else:
            data['telno'] = ''
        datematch = self.datere.search(self.message)
        if datematch:
            data['date'] = datematch.group(1)
            try:
                data['date']  = datetime.datetime.strptime(data['date'], '%Y%m%dT%H%M%SZ')
            except ValueError:
                # Use Epoch as date if no date was available
                data['date'] = datetime.datetime.strptime('1970-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
        bodymatch = self.bodyre.search(self.message)
        if bodymatch:
            data['body'] = escapexml(bodymatch.group(1))[:-1]
        else:
            data['body'] = ''
        return data
        
class Writer(object):
    """Base class for a writer object to convert all VMG files to a single file
    """
    def __init__(self, filename):
        """Create a file writer object with the filename specified
        """
        self.filename = filename
        self.file = open(filename, 'w')

    def processdir(self, dirpath):
        """Given a directory path, process all the .vmg files in it and store as a list
        """
        files = glob.glob(dirpath + '/*.vmg')
        reader = VMGReader()
        self.messages = []
        for f in files:
            print f
            reader.read(f)
            self.messages.append(reader.process())
        self.messages.sort(datecmp)     # Sort the messages according to date
            
class XMLWriter(Writer):
    """Writer object for XML file as output
    """
    def write(self):
        """Read every message in the list and write to a XML file
        """
        self.file.write('<messages>')
        tmpl = "<message><tel>%s</tel><date>%s</date><body>%s</body></message>"
        for msg in self.messages:
            xmlstr = tmpl %(msg['telno'], msg['date'].strftime('%Y-%m-%d %H:%M:%S'), msg['body'])
            self.file.write(xmlstr)
        self.file.write('</messages>')
        self.file.close()
        
