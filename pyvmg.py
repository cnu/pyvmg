import re
import datetime

class VMGReader(object):
    def __init__(self):
        self.telre = re.compile(r'TEL:(\+?\d+)')
        self.datere = re.compile(r'X-NOK-DT:([\dTZ]+)')
        self.bodyre = re.compile(r'Date:[\d.: ]+\n(.*)END:VBODY',re.DOTALL)
    
    def read(self, filename):
        self.filename = filename
        self.message = open(filename, 'r').read()
        self.message = self.message.replace('\0', '')

    def process(self):
        data = {}
        data['telno'] = self.telre.search(self.message).group(1)
        data['date'] = self.datere.search(self.message).group(1)
        data['date']  = datetime.datetime.strptime(data['date'], '%Y%m%dT%H%M%SZ')
        data['body'] = self.bodyre.search(self.message).group(1)
        return data
        
        
