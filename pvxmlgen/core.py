from pkg_resources import parse_version
from subprocess import check_output, Popen, PIPE
import tempfile
import os
from glob import iglob
import xml.etree.ElementTree as ET


DOXYGEN_EXECUTABLE = 'doxygen'
DOXYGEN_MIN_VERSION = '1.8'
DOXYGEN_CFG = r"""
GENERATE_HTML          = NO
GENERATE_LATEX         = NO
GENERATE_MAN           = NO
GENERATE_RTF           = NO
GENERATE_XML           = YES
XML_OUTPUT             = "{outdir}"
XML_PROGRAMLISTING     = NO
EXTRACT_ALL            = YES
ENABLE_PREPROCESSING   = NO
QUIET                  = NO
ALIASES               += pv_begin="@xmlonly<paraview type=\"insert\">\n"
ALIASES               += pv_begin{{1}}="@xmlonly<paraview type=\"\1\">\n"
ALIASES               += pv_end="</paraview>\n@endxmlonly"
ALIASES               += pv_plugin{{1}}="@xmlonly<paraview proxygroup=\"\1\" />\n@endxmlonly"
ALIASES               += pv_attr{{2}}="@xmlonly<paraview type=\"attribute\" name=\"\1\" value=\"\2\" />\n@endxmlonly"
ALIASES               += pv_member="@xmlonly<paraview/>@endxmlonly"
INPUT                  = {input}
""".strip()


def doxygen_version():
    try:
        doxygen_version = check_output([DOXYGEN_EXECUTABLE, "-v"]).decode('utf-8')
    except OSError:
        return None
    doxygen_version = parse_version(doxygen_version)
    if doxygen_version < parse_version(DOXYGEN_MIN_VERSION):
        return None
    return doxygen_version


def doxygen_execute(files):
    xmlnodes = []
    inputs = ' '.join('"' + os.path.abspath(filename) + '"' for filename in files)
    with tempfile.TemporaryDirectory() as tmpdirname:        
        doxygen_config = DOXYGEN_CFG.format(input=inputs, outdir=tmpdirname).encode('utf-8')
        doxygen = Popen(['doxygen', '-'], cwd=tmpdirname, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        doxygen_output, doxygen_error = doxygen.communicate(input=doxygen_config)
        if doxygen.returncode != 0:            
            print(doxygen_output.decode('utf-8'))
            print(doxygen_error.decode('utf-8'))
            print('Error while executing doxygen')

        for xmlfile in iglob(os.path.join(tmpdirname, 'class*.xml')):
            try:
                root = ET.parse(xmlfile).getroot()
                xmlnodes.append((xmlfile, root))
            except ET.ParseError:
                print('Error parsing {}'.format(xmlfile))            

    return xmlnodes


def doxygen_parse_classes(xmlnodes):
    classes = {}
    for filename, root in xmlnodes:
        try:
            root = root.find('compounddef')
            class_name = root.find('compoundname').text
            if class_name in classes:
                print('Found duplicate class name: {}'.format(class_name))
                continue
            if root.attrib['kind'] != 'class':
                print('Not a class: {}'.format(class_name))
                continue
            class_defs = list(root.find('detaileddescription').iter('paraview'))
            if not class_defs:
                print('Class skipped: {}'.format(class_name))
                continue
            paraview_defs = {}
            paraview_defs['defs'] = class_defs
            paraview_defs['members'] = {}

            for member in root.iter('memberdef'):
                detaileddescription = member.find('detaileddescription')
                if not detaileddescription:
                    continue
                member_defs = list(detaileddescription.iter('paraview'))
                if member_defs:
                    name = member.find('name').text
                    if name in paraview_defs['members'].keys():
                        print('Found duplicate member name: {}'.format(name))
                        continue
                    member_type = member.find('type').text
                    if member_type not in ['int', 'double', 'bool']:
                        print('Member ({}) has unsupported type: {}'.format(name, member_type))
                        continue
                    paraview_defs['members'][name] = {}
                    paraview_defs['members'][name]['type'] = member_type
                    paraview_defs['members'][name]['argsstring'] = member.find('argsstring').text
                    paraview_defs['members'][name]['initializer'] = member.find('initializer').text
                    paraview_defs['members'][name]['defs'] = member_defs

            classes[class_name] = paraview_defs
        except AttributeError:
            print('Error parsing {}'.format(filename))
            pass
    return classes
