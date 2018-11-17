import xml.etree.ElementTree as ET
import re
import traceback
import sys
import xml_state
from collections import namedtuple


def indent(elem, indentation=4 * ' ', level=0):
    i = '\n' + level * indentation
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + indentation
        for e in elem:
            indent(e, indentation, level + 1)
            if not e.tail or not e.tail.strip():
                e.tail = i + indentation
        if not e.tail or not e.tail.strip():
            e.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
    if len(elem.attrib) > 2:
        elem.attrib = {(i + indentation + k): v for k, v in elem.attrib.items()}


Block = namedtuple('Block', ['content', 'context', 'line'])


def parse_file(s):
    result = []
    left = s.split('pv_(')
    for i, part in enumerate(left):
        if i == 0:
            continue
        current_line = len('pv_('.join(left[:i]).splitlines())

        right = part.split(')pv_')
        if len(right) < 2:
            raise Exception('"pv_(" in {}:{} has no matching ")pv_".'.format(filename, current_line))
        elif len(right) > 2:
            raise Exception('"pv_(" in {}:{} has multiple ")pv_".'.format(filename, current_line))

        content_lines = right[0].splitlines()
        while len(content_lines) > 0  and content_lines[0].strip() == '':
            current_line += 1
            content_lines = content_lines[1:]
        content = right[0].strip()

        context = right[1].splitlines()
        if len(context) >= 2:
            context = context[1]
        else:
            context = None

        result.append(Block(content, context, current_line))

    return result


def parse_declaration(s):
    context_dict = {}
    if s is None:
        return context_dict

    if ';' in s:
        declaration = s.split(';')[0]

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

        context_dict['name'] = name
        context_dict['type'] = data_type
        context_dict['number_of_elements'] = number_of_elements
        if default_values is not None:
            context_dict['default_values'] = default_values

    elif 'class' in s:
        declaration = re.split(r'\:|\{', s)[0]
        declaration = declaration.split()[-1]
        context_dict['class'] = declaration

    return context_dict


if __name__ == '__main__':
    filename = '../prtl/include/prtl/vtk/prtlModel.h'

    with open(filename) as f:
        s = f.read()
    try:
        blocks = parse_file(s)
    except Exception as e:
        print(e)
        quit(1)

    root = xml_state.XMLNode()
    current = root

    try:
        for block in blocks:
            current.context = parse_declaration(block.context)
            namespace = { 'current': current }
            current = eval('current.' + block.content, namespace)
    except Exception as e:
        print('Error processing {}:{}:'.format(filename, block.line))
        if hasattr(e, 'lineno'):
            e.filename = filename
            e.lineno += block.line - 1
            try:
                raise e
            except:
                pass            
            traceback.print_exc(limit=0)
        else:
            print(e)
        quit(1)

    indent(root)
    print(ET.tostring(root, encoding='utf-8').decode('utf-8'))
