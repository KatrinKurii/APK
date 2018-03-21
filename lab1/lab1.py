from xml.dom.minidom import parse
from datetime import datetime
import sys

program_type_all = 'Всі'
program_type_default = 'Серіали'


def get_files(path_xml):
    xmldoc = parse(path_xml)
    items = xmldoc.getElementsByTagName('item')
    files = [(t.childNodes[0].data, t.attributes['name'].value) for t in items]
    xmldoc.unlink()
    return files


def get_timetable(path_html):
    htmldoc = parse(path_html)
    timetable = []

    for tr in htmldoc.getElementsByTagName('tr'):
        tds = tr.getElementsByTagName('td')
        program = [td.childNodes[0].data for td in tds]
        if (program):
            timetable.append(program)

    htmldoc.unlink()
    return timetable


def printChannel(channel):
    print(channel[0])
    for prog in channel[1]:
        print('   ' + prog[0] + ' - ' + prog[1] + ' (' + prog[2] + ')')


def filterDate(timetable, start, end):
    filtered = []
    for program in timetable:
        current = datetime.strptime(program[0], '%d.%m.%Y %H:%M')
        if (current >= start and current <= end):
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
    if type_str and type_str != program_type_all:
        filtered = filterType(filtered, type_str)

    return filtered


if __name__ == '__main__':
    channels = get_files('channels.xml')
    timetables = [(ch[1], get_timetable(ch[0])) for ch in channels]

    datetime_start = sys.argv[1] if len(sys.argv) >= 2 else None
    datetime_end = sys.argv[2] if len(sys.argv) >= 3 else None
    program_type = sys.argv[3] if len(sys.argv) >= 4 else None

    if datetime_start:
        try:
            datetime_start = datetime.strptime(datetime_start,
                                               '%d.%m.%Y %H:%M')
        except ValueError:
            sys.exit('Невірно введена перша дата')

    if datetime_end:
        try:
            datetime_end = datetime.strptime(datetime_end, '%d.%m.%Y %H:%M')
        except ValueError:
            sys.exit('Невірно введена друга дата')

    if not program_type:
        program_type = program_type_default

    filtered_timetables = []
    for timetable in timetables:
        filtered_channel = filter(timetable[1],
                                  datetime_start,
                                  datetime_end,
                                  program_type)
        filtered_timetables.append((timetable[0], filtered_channel))

    i = 0
    print('Результат пошуку:')
    for channel in filtered_timetables:
        if channel[1]:
            i += 1
            print(str(i) + '. ', end='')
            printChannel(channel)
            print()

    if i == 0:
        print('    ** None **')
