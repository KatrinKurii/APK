from xml.dom.minidom import parse

def get_timetable(path_html):
    htmldoc = parse(path_html)
    timetable = []

    for tr in htmldoc.getElementsByTagName('tr'):
        program = [td.childNodes[0].data for td in tr.getElementsByTagName('td')]
        if (program):
            timetable.append(program)
    
    htmldoc.unlink()
    return timetable

def get_files(path_xml):
    xmldoc = parse(path_xml)
    items = xmldoc.getElementsByTagName('item')
    files = [(item.childNodes[0].data, item.attributes['name'].value) for item in items]
    xmldoc.unlink()
    return files

def printProgram(program):
    print(program[0] + ' - ' + program[1] + ' (' + program[2] + ')')

def printChannel(channel):
    print(channel[0])
    for program in channel[1]:
        print('   ', end = '')
        printProgram(program)

def filterDate(timetable, start, end):
    filtered = timetable
    return filtered

def filterType(timetable, type):
    filtered = timetable
    return filtered

def filter(timetable, date_start, date_end, type_str):
    filtered = filterDate(timetable, date_start, date_end)
    filtered = filterType(filtered, type_str)
    return filtered

if __name__ == '__main__':
    channels = get_files('channels.xml')
    timetables = [(channel[1], get_timetable(channel[0])) for channel in channels]
    
    for i, channel in enumerate(timetables):
        print(str(i + 1) + '. ', end = '')
        printChannel(channel)
        print()
