import xml.etree.ElementTree as ET
import re
import traceback
import sys
import xml_state

class ParserError(Exception):
    pass

def indent(elem, indentation=4 * ' ', level=0):
    i = '\n' + level * indentation
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + indentation
        for e in elem:
            indent(e, indentation, level+1)
            if not e.tail or not e.tail.strip():
                e.tail = i + indentation
        if not e.tail or not e.tail.strip():
            e.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
    if len(elem.attrib) > 2:
        elem.attrib = {(i + indentation + k): v for k, v in elem.attrib.items()}


filename = '../prtl/include/prtl/vtk/prtlModel.h'

with open(filename) as f:
    s = f.read()


root = xml_state.XMLNode()
current = root

left = s.split('pv_(')
for i, part in enumerate(left):
    if i == 0:
        continue
    current_line = len('pv_('.join(left[:i]).splitlines())

    right = part.split(')pv_')
    if len(right) != 2:
        print('Error: "pv_(" in line {}:{} has no matching ")pv_".'.format(filename, current_line))
        quit(1)

    content = right[0].lstrip()

    context_dict = {}
    context = right[1].splitlines()
    if len(context) >= 2:
        declaration = context[1].split(';')
        declaration = declaration[0] if len(declaration) > 1 else None

        if declaration is not None:
            data_type, name = declaration.split()[:2]
            name = re.split(r'\[|\{', name)[0]
            number_of_elements = re.search(r'\[(.*?)\]', declaration)
            number_of_elements = eval(number_of_elements.group(1)) if number_of_elements else 1
            default_values = re.search(r'\{(.*?)\}', declaration)
            if default_values:
                default_values = default_values.group(1)
                default_values = default_values.replace('false', 'False')
                default_values = default_values.replace('true', 'True')
                default_values = eval('({})'.format(default_values))
            else:
                default_values = None

            current_line += len(content.splitlines())

            context_dict['name'] = name
            context_dict['type'] = data_type
            context_dict['number_of_elements'] = number_of_elements
            if default_values is not None:
                context_dict['default_values'] = default_values
        elif 'class' in context[1]:
            declaration = re.split(r'\:|\{', context[1])[0]
            declaration = declaration.split()[-1]
            context_dict['class'] = declaration

    current.context = context_dict
    namespace = { 'current': current }
    namespace.update(xml_state.__dict__)
    try:
        current = eval('current.' + content, namespace)
    except Exception as e:
        if hasattr(e, 'filename'):
            e.filename = filename
        if hasattr(e, 'lineno'):
            e.lineno += current_line - 1
        try:
            raise e
        except:
            pass
        print('Error processing {}:{}:\n'.format(filename, current_line))
        traceback.print_exc(limit=0)
        quit(1)

indent(root)
print(ET.tostring(root, encoding='utf-8').decode('utf-8'))
