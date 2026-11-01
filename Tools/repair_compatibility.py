from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from xml.etree import ElementTree as E
import openpyxl

root=Path(__file__).parent
files=[root/'travel_times_sample.xlsx',root/'restaurant_wait_times_sample.xlsx']
backup=root/'Backups';backup.mkdir(exist_ok=True)
with ZipFile(backup/'before_compatibility_repair.zip','x',ZIP_DEFLATED) as z:
    for p in files:z.write(p,p.name)
ns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
q=lambda x:'{'+ns+'}'+x
E.register_namespace('x',ns)
for p in files:
    before=openpyxl.load_workbook(p)
    values={s.title:list(s.values) for s in before}
    with ZipFile(p) as z:parts={n:z.read(n) for n in z.namelist()}
    for name,data in list(parts.items()):
        if name.startswith('xl/worksheets/') and name.endswith('.xml'):
            xml=E.fromstring(data)
            for c in xml.iter(q('c')):
                if c.get('t')=='str' and c.find(q('f')) is None:
                    v=c.find(q('v')); text=v.text or ''
                    c.remove(v);c.set('t','inlineStr')
                    t=E.SubElement(E.SubElement(c,q('is')),q('t'));t.text=text
                    if text.strip()!=text:t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
            parts[name]=E.tostring(xml,encoding='utf-8',xml_declaration=True)
    name='xl/workbook.xml';xml=E.fromstring(parts[name])
    if xml.find(q('bookViews')) is None:
        views=E.Element(q('bookViews'));E.SubElement(views,q('workbookView'),activeTab='0')
        xml.insert(0,views)
    parts[name]=E.tostring(xml,encoding='utf-8',xml_declaration=True)
    if p.name.startswith('travel'):
        name='xl/tables/table1.xml';xml=E.fromstring(parts[name])
        xml.find(q('tableColumns'))[2].set('name','walk distance (min)')
        parts[name]=E.tostring(xml,encoding='utf-8',xml_declaration=True)
    temp=p.with_suffix('.tmp.xlsx')
    with ZipFile(temp,'w',ZIP_DEFLATED) as z:
        for name,data in parts.items():z.writestr(name,data)
    after=openpyxl.load_workbook(temp)
    assert values=={s.title:list(s.values) for s in after}
    for s in after:
        for table in s.tables.values():
            headers=[c.value for c in s[1]][:len(table.tableColumns)]
            assert headers==[c.name for c in table.tableColumns]
    with ZipFile(temp) as z:assert z.testzip() is None
    temp.replace(p)
    print(p.name+': repaired; all cell values and table headers verified')
