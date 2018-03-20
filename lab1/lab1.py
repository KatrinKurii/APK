from xml.dom.minidom import parse
from datetime import datetime

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
    filtered = []
    datetime_start = datetime.strptime(start, '%d.%m.%Y %H:%M')
    datetime_end = datetime.strptime(end, '%d.%m.%Y %H:%M')
    for program in timetable:
        datetime_current = datetime.strptime(program[0], '%d.%m.%Y %H:%M')
        if ((datetime_current >= datetime_start) and (datetime_current <= datetime_end)):
            filtered.append(program)

    return filtered

def filterType(timetable, type):
    filtered = []
    for program in timetable:
        if (program[2] == type):
            filtered.append(program)

    return filtered

def filter(timetable, date_start, date_end, type_str):
    filtered = filterDate(timetable, date_start, date_end)
    filtered = filterType(filtered, type_str)
    return filtered

if __name__ == '__main__':
    channels = get_files('channels.xml')
    timetables = [(channel[1], get_timetable(channel[0])) for channel in channels]
    filtered_timetable = [[timetable[0], filter(timetable[1], '19.03.2018 06:29', '22.03.2018 10:29', 'Серіали')] for timetable in timetables]

    for i, channel in enumerate(filtered_timetable):
        if channel[1]:
            print(str(i + 1) + '. ', end = '')
            printChannel(channel)
            print()
