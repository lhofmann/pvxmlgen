from pkg_resources import parse_version
from subprocess import check_output, Popen, PIPE
import tempfile
import os
from glob import iglob
import xml.etree.ElementTree as ET
import re


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
ALIASES               += pv_begin_insert="@xmlonly<paraview type=\"insert\">\n"
ALIASES               += pv_begin_append="@xmlonly<paraview type=\"append">\n"
ALIASES               += pv_end="</paraview>\n@endxmlonly"
ALIASES               += pv_plugin{{1}}="@xmlonly<paraview type=\"proxygroup\" value=\"\1\" />\n@endxmlonly"
ALIASES               += pv_attr{{2}}="@xmlonly<paraview type=\"attribute\" name=\"\1\" value=\"\2\" />\n@endxmlonly"
ALIASES               += pv_member="@xmlonly<paraview/>@endxmlonly"
ALIASES               += pv_member{{1}}="@xmlonly<paraview type=\"attribute\" name=\"label\" value=\"\1\" />@endxmlonly"
INPUT                  = {input}
""".strip()
TYPE_XML_TAG = {
    'int': 'IntVectorProperty',
    'bool': 'IntVectorProperty',
    'char *': 'StringVectorProperty',
    'double': 'DoubleVectorProperty',
}


def doxygen_version():
    try:
        doxygen_version = check_output([DOXYGEN_EXECUTABLE, "-v"]).decode('utf-8')
        return parse_version(doxygen_version)
    except (OSError, TypeError):
        return None


def doxygen_execute(files):
    xmlnodes = []
    inputs = ' '.join('"' + os.path.abspath(filename) + '"' for filename in files)
    with tempfile.TemporaryDirectory() as tmpdirname:
        doxygen_config = DOXYGEN_CFG.format(input=inputs, outdir=tmpdirname).encode('utf-8')
        doxygen = Popen([DOXYGEN_EXECUTABLE, '-'], cwd=tmpdirname, stdout=PIPE, stdin=PIPE, stderr=PIPE)
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
                    if member_type not in TYPE_XML_TAG.keys():
                        print('Member ({}) has unsupported type: {}'.format(name, member_type))
                        continue
                    paraview_defs['members'][name] = {}
                    paraview_defs['members'][name]['type'] = member_type
                    argsstring = member.find('argsstring')
                    paraview_defs['members'][name]['argsstring'] = None if argsstring is None else argsstring.text
                    initializer = member.find('initializer')
                    paraview_defs['members'][name]['initializer'] = None if initializer is None else initializer.text
                    paraview_defs['members'][name]['defs'] = member_defs

            classes[class_name] = paraview_defs
        except AttributeError:
            print('Error parsing {}'.format(filename))
            pass
    return classes


def parse_argsstring(argsstring):
    if not argsstring:
        return 1
    argsstring = argsstring.strip()
    if not argsstring:
        return 1
    number = re.match(r'^\[\s*(\d+)\s*\]$', argsstring)
    if not number:
        print('Unable to parse array length: {}'.format(argsstring))
        return None
    if int(number.group(1)) <= 0:
        print('Unexpected array length: {}'.format(argsstring))
        return None
    return int(number.group(1))


def parse_initializer(initializer, value_type, number_of_elements):
    initializer = initializer.strip()
    initializer_input = initializer
    is_initializer_list = False
    if not initializer:
        return ''
    if initializer[0] == '=':
        initializer = initializer[1:].strip()
    if not initializer:
        print('Expected value after "=": {}'.format(initializer_input))
        return None
    if (initializer[0] == '{') != (initializer[-1] == '}'):
        print('Non-matching brackets: {}'.format(initializer_input))
        return None
    if initializer[0] == '{':
        initializer = initializer[1:-1]
        is_initializer_list = True
    initializer = initializer.split(',')
    if len(initializer) > 1 and not is_initializer_list:
        print('Unexpected list: {}'.format(initializer_input))
        return None
    if len(initializer) != number_of_elements:
        print('Unexpected number of values: {}'.format(initializer_input))
        return None
    for i, value in enumerate(initializer):
        value = value.strip()
        if value_type == 'bool':
            if value.lower() == 'true' or value == '1':
                value = '1'
            elif value.lower() == 'false' or value == '0':
                value = '0'
            else:
                print('Invalid boolean value: {}'.format(value))
                return None
        elif value_type == 'int':
            if not re.match(r'^[\+|-]?\d+$', value):
                print('Invalid integer value: {}'.format(value))
                return None
        elif value_type == 'double':
            if not re.match(r'^[+-]?(?=[.]?[0-9])[0-9]*(?:[.][0-9]*)?(?:[Ee][+-]?[0-9]+)?$', value):
                print('Invalid floating point value: {}'.format(value))
                return None
        elif value_type == 'char *':
            if value.lower() in ['0', 'null', 'nullptr']:
                value = ''
            elif value[0] == '"' and value[-1] == '"':
                value = value[1:-1]
            else:
                print('Invalid string value: {}'.format(value))
                return None
        initializer[i] = value
    return ' '.join(initializer)


def parse_xml_command(command):
    command_type, name, value = None, None, None
    if 'type' in command.attrib.keys():
        command_type = command.attrib['type']
        if 'name' in command.attrib.keys():
            name = command.attrib['name']
        if 'value' in command.attrib.keys():
            value = command.attrib['value']
    return command_type, name, value


def execute_class_command(parent, node, command):
    command_type, name, value = parse_xml_command(command)
    if (command_type == 'proxygroup') and (value is not None):
        parent.attrib['name'] = value
    elif (command_type == 'attribute') and (name is not None) and (value is not None):
        node.attrib[name] = value.strip()
    elif (command_type == 'insert'):
        for child in command:
            node.append(child)
    elif command_type is not None:
        print('Unrecognized class command: ({}, {}, {})'.format(command_type, name, value))


def execute_member_command(parent, node, command):
    command_type, name, value = parse_xml_command(command)
    if (command_type == 'attribute') and (name is not None) and (value is not None):
        node.attrib[name] = value.strip()
    elif (command_type == 'insert'):
        for child in command:
            node.append(child)
    elif (command_type == 'append'):
        for child in command:
            parent.append(child)
    elif command_type is not None:
        print('Unrecognized class command: ({}, {}, {})'.format(command_type, name, value))


def paraview_class_xml(class_name, paraview_defs):
    root = ET.Element('ServerManagerConfiguration')
    proxygroup = ET.SubElement(root, 'ProxyGroup')
    sourceproxy = ET.SubElement(proxygroup, 'SourceProxy')
    sourceproxy.attrib['class'] = class_name
    class_label = class_name
    if class_label.startswith('vtk'):
        class_label = class_label[3:]
    sourceproxy.attrib['label'] = class_label
    sourceproxy.attrib['name'] = class_label
    for command in paraview_defs['defs']:
        execute_class_command(proxygroup, sourceproxy, command)
    for member_name, info in paraview_defs['members'].items():
        member_node = ET.SubElement(sourceproxy, TYPE_XML_TAG[info['type']])
        member_node.attrib['name'] = member_name
        member_node.attrib['command'] = 'Set' + member_name
        member_node.attrib['label'] = member_name
        number_of_elements = parse_argsstring(info['argsstring'])
        if number_of_elements is None:
            return None
        member_node.attrib['number_of_elements'] = str(number_of_elements)
        if info['type'] == 'bool':
            domain = ET.SubElement(member_node, 'BooleanDomain')
            domain.attrib['name'] = 'bool'
        if info['initializer']:
            default_values = parse_initializer(info['initializer'], info['type'], number_of_elements)
            if default_values is None:
                return None
            if default_values:
                member_node.attrib['default_values'] = default_values
        for command in info['defs']:
            execute_member_command(sourceproxy, member_node, command)
    return root


def merge_class_xml(class_xml, target):
    # TODO
    pass
