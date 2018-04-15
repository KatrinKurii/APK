import urllib.request
from xml.dom.minidom import parse, parseString
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, date
import sys
import xml.etree.ElementTree as ET
from re import search

program_type_all = 'Всі'
program_type_default = 'Т/с'


def get_urls(path_xml):
    xmldoc = parse(path_xml)
    items = xmldoc.getElementsByTagName('item')
    urls = [(t.childNodes[0].data, t.attributes['name'].value) for t in items]
    xmldoc.unlink()
    return urls


def get_programs(url):
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    text = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(text, "html.parser")
    trs_list = [td.parent for td in soup.findAll('td', {'class': 'item'})]

    program_list = []
    for tr in trs_list:
        program_list.append({'time': tr.find('td', {'class': 'time'}).text,
                             'name': tr.find('td', {'class': 'item'})})
        buff = program_list[-1]['name'].find('a')
        if buff:
            program_list[-1]['name'] = buff.text
        else:
            program_list[-1]['name'] = program_list[-1]['name'].text

    return program_list


def define_types(program_list):
    for program in program_list:
        searchObj = search(r'(\w{1}/\w{1})* *\"*([^\"]+)\"*', program['name'])
        program['name'] = searchObj.group(2)
        program['type'] = searchObj.group(1) if searchObj.group(1) else 'Т/ш'
    return program_list


def define_date(program_list, datetime):
    for program in program_list:
        program['time'] = datetime.strftime("%Y-%m-%d") + ' ' + program['time']
    return program_list


def filter(timetable, filter_type=program_type_default):
    result = []
    for program in timetable:
        if program['type'] == filter_type:
            result.append(program)
    return result


def daterange(datetime_start, datetime_end):
    for n in range(int((datetime_end - datetime_start).days)):
        yield datetime_start + timedelta(n)


def get_programs_by_datetimes(url, datetime_start, datetime_end):
    date_str = datetime_start.strftime("%d%m%Y")
    return define_date(define_types(get_programs(url + date_str)),
                       datetime_start)


def get_channel_timetable(url, datetime_start, datetime_end, filter_type):
    timetable = []

    if (datetime_end - datetime_start).days > 1:
        replace_str = datetime_start.replace(hour=23, minute=59)
        timetable = get_programs_by_datetimes(url,
                                              datetime_start,
                                              replace_str)

        next_day = datetime_start.replace(day=datetime_start.day + 1,
                                          hour=0, minute=0)
        for datetime in daterange(next_day,
                                  datetime_end.replace(hour=0, minute=0)):

            rep = datetime.replace(hour=23, minute=59)
            timetable += get_programs_by_datetimes(url,
                                                   datetime,
                                                   rep)

        rep = datetime_end.replace(hour=0, minute=0)
        timetable += get_programs_by_datetimes(url,
                                               rep,
                                               datetime_end)
    else:
        timetable = get_programs_by_datetimes(url,
                                              datetime_start,
                                              datetime_end)

    if filter_type != program_type_all:
        timetable = filter(timetable, filter_type)

    return timetable


def createXML(timetables):
    channels = ET.Element('channels')
    for ch in timetables:
        if ch[1]:
            channel = ET.SubElement(channels, 'channel')
            channel.set('name', ch[0])
            for pr in ch[1]:
                program = ET.SubElement(channel, 'program')
                date = ET.SubElement(program, 'date')
                name = ET.SubElement(program, 'name')
                type = ET.SubElement(program, 'type')

                date.text = pr['time']
                name.text = pr['name']
                type.text = pr['type']

    xmlstr = parseString(ET.tostring(channels)).toprettyxml(indent="   ")
    with open("output.xml", "w") as f:
        f.write(xmlstr)


if __name__ == '__main__':
    datetime_start = None
    datetime_end = None
    program_type = None

    if len(sys.argv) == 1:
        datetime_start = datetime.now().strftime('%d.%m.%Y %H:%M')
        datetime_end = datetime_start[:-5] + '23:59'

    if len(sys.argv) == 2:
        datetime_start = sys.argv[1]
        datetime_end = datetime_start[:-5] + '23:59'

    if len(sys.argv) >= 3:
        datetime_start = sys.argv[1]
        datetime_end = sys.argv[2]

    if len(sys.argv) >= 4:
        program_type = sys.argv[3]

    urls = get_urls('channels.xml')
    if not urls:
        sys.exit('Error!\nПустий вхідний XML файл')

    if datetime_start:
        try:
            datetime_start = datetime.strptime(datetime_start,
                                               '%d.%m.%Y %H:%M')
        except ValueError:
            sys.exit('Error!\nНевірно введена перша дата')

    if datetime_end:
        try:
            datetime_end = datetime.strptime(datetime_end, '%d.%m.%Y %H:%M')
        except ValueError:
            sys.exit('Error!\nНевірно введена друга дата')

    if datetime_start > datetime_end:
        sys.exit('Error!\nНевірний порядок дат')

    if not program_type:
        program_type = program_type_default

    timetables = [(url[1], get_channel_timetable(url[0],
                                                 datetime_start,
                                                 datetime_end,
                                                 program_type))
                  for url in urls]
    createXML(timetables)
