from xml.dom.minidom import parse
from datetime import datetime

program_type_all = 'Всі'
program_type_default = 'Серіали'

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

def printChannel(channel):
    print(channel[0])
    for program in channel[1]:
        print('   ' + program[0] + ' - ' + program[1] + ' (' + program[2] + ')')

def filterDate(timetable, datetime_start, datetime_end):
    filtered = []
    for program in timetable:
        datetime_current = datetime.strptime(program[0], '%d.%m.%Y %H:%M')
        if (datetime_current >= datetime_start and datetime_current <= datetime_end):
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

def getAllTypes(timetables):
    types = set()
    for timetable in timetables:
        for program in timetable[1]:
            types.add(program[2])

    return types

def getMinDate(timetables):
    datetime_min = None;
    for timetable in timetables:
        for program in timetable[1]:
            datetime_current = datetime.strptime(program[0], '%d.%m.%Y %H:%M')
            if not datetime_min or datetime_current < datetime_min:
                datetime_min = datetime_current
    return datetime_min.strftime('%d.%m.%Y %H:%M')


def getMaxDate(timetables):
    datetime_max = None;
    for timetable in timetables:
        for program in timetable[1]:
            datetime_current = datetime.strptime(program[0], '%d.%m.%Y %H:%M')
            if not datetime_max or datetime_current > datetime_max:
                datetime_max = datetime_current
    return datetime_max.strftime('%d.%m.%Y %H:%M')

if __name__ == '__main__':
    channels = get_files('channels.xml')
    timetables = [(channel[1], get_timetable(channel[0])) for channel in channels]
    datetime_min = getMinDate(timetables)
    datetime_max = getMaxDate(timetables)

    print('Типи передач: ' + ', '.join(str(type) for type in getAllTypes(timetables)))

    while True:
        print('Введіть першу дату[' + str(datetime_min) + ']: ', end = '')
        datetime_start = input()
        if not datetime_start:
            datetime_start = datetime_min

        try:
            datetime_start = datetime.strptime(datetime_start, '%d.%m.%Y %H:%M')
        except ValueError:
            print('Невірно введена дата, спробуйте ще раз')
        except:
            exit()
        else:
            if not datetime_start:
                datetime_start = datetime_min
            break

    while True:
        print('Введіть другу дату[' + str(datetime_max) + ']: ', end = '')
        datetime_end = input()
        if not datetime_end:
            datetime_end = datetime_max
            
        try:
            datetime_end = datetime.strptime(datetime_end, '%d.%m.%Y %H:%M')
        except ValueError:
            print('Невірно введена дата, спробуйте ще раз')
        except:
            exit()
        else:
            if not datetime_end:
                datetime_end = datetime_max
            break

    print('Введіть тип телепрограми[' + program_type_default + ']: ',  end = '')
    program_type = input()
    if not program_type:
        program_type = program_type_default

    filtered_timetable = [(timetable[0], filter(timetable[1], datetime_start, datetime_end, program_type)) for timetable in timetables]

    print('\nРезультат пошуку:')
    i = 0
    for channel in filtered_timetable:
        if channel[1]:
            i += 1
            print(str(i) + '. ', end = '')
            printChannel(channel)
            print()
    
    if i == 0:
        print('    ** None **')
