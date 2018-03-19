from xml.dom.minidom import parse

class TimeTable:
    def __init__(self, path_html):
        htmldoc = parse(path_html)
        self.timetable = []
        for program in htmldoc.getElementsByTagName('tr'):
            prog = []
            for td in program.getElementsByTagName('td'):
                prog.append(td.childNodes[0].data)
                
            if (prog):
                self.timetable.append(prog)
        
        print(self.timetable)
        htmldoc.unlink()

    def get_timetable(self):
        return self.timetable

def get_files(path_xml):
    xmldoc = parse(path_xml)
    items = xmldoc.getElementsByTagName('item')
    files = [(item.childNodes[0].data, item.attributes['name'].value) for item in items]
    xmldoc.unlink()
    return files

if __name__ == '__main__':
    channels = get_files('channels.xml')
    timetables = [(channel[1], TimeTable(channel[0]).get_timetable()) for channel in channels]
    
    for channel in timetables:
        print(channel)
