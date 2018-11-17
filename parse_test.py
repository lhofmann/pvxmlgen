import xml.etree.ElementTree as ET
import re
import traceback
import sys
import xml_state
from collections import namedtuple


class ParserException(BaseException):
    def __init__(self, exception, line=None):
        self.exception = exception
        self.line = line
        if hasattr(self.exception, 'lineno'):
            self.exception.lineno += self.line - 1

    def __str__(self):
        return str(self.exception)


Block = namedtuple('Block', ['content', 'context', 'line_content', 'line_context'])


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


def parse_file(s):
    result = []
    left = s.split('pv_(')
    for i, part in enumerate(left):
        if i == 0:
            continue
        current_line = len('pv_('.join(left[:i]).splitlines())

        right = part.split(')pv_')
        if len(right) < 2:
            raise Exception('"pv_(" in line {} has no matching ")pv_".'.format(current_line))
        elif len(right) > 2:
            raise Exception('"pv_(" in line {} has multiple ")pv_".'.format(current_line))

        content_lines = right[0].splitlines()
        while len(content_lines) > 0  and content_lines[0].strip() == '':
            current_line += 1
            content_lines = content_lines[1:]
        content = right[0].strip()

        context_line = current_line + len(content.splitlines())
        context = right[1].splitlines()
        if len(context) >= 2:
            context = context[1]
        else:
            context = None

        result.append(Block(content, context, current_line, context_line))

    return result


def parse_declaration(s):
    context_dict = {}
    if s is None:
        return context_dict

    # variable declaration
    if ';' in s:
        declaration = s.split(';')[0]

        # find type and name as whitespace-separated list left of '=', '{', or '['
        lhs = re.split(r'[=\[\{]', declaration)[0].split()
        if len(lhs) < 2:
            raise Exception('Cannot determine variable type and name.')
        data_type = ' '.join(lhs[:-1])
        name = lhs[-1]

        # find array declaration
        number_of_elements = re.search(r'\[(.*?)\]', declaration)
        number_of_elements = eval(number_of_elements.group(1)) if number_of_elements else 1

        # find initializer-list and default-initialization
        default_values = re.search(r'\{(.*?)\}', declaration)
        if default_values:
            default_values = default_values.group(1)
        elif '=' in declaration:
            default_values = declaration.split('=')[-1]
        else:
            default_values = None

        if default_values is not None:
            # rename boolean values if not a string
            if '"' not in default_values:
                default_values = default_values.replace('false', 'False')
                default_values = default_values.replace('true', 'True')
            default_values = eval('({})'.format(default_values))            

        context_dict['name'] = name
        context_dict['type'] = data_type
        context_dict['number_of_elements'] = number_of_elements
        if default_values is not None:
            context_dict['default_values'] = default_values

    # class definition
    elif 'class' in s:
        # class name should be the right-most word left of ':' or '{'
        declaration = re.split(r'\:|\{', s)[0]
        declaration = declaration.split()[-1]
        context_dict['class'] = declaration

    return context_dict


def generate_xml(s):
    blocks = parse_file(s)
    root = xml_state.XMLNode()
    current = root

    for block in blocks:
        try:
            current.context = parse_declaration(block.context)
        except Exception as e:
            raise ParserException(e, block.line_context)
        namespace = { 'current': current }
        try:
            current = eval('current.' + block.content, namespace)    
        except Exception as e:
            raise ParserException(e, block.line_content)

    return root    


if __name__ == '__main__':
    filename = '../prtl/include/prtl/vtk/prtlModel.h'

    with open(filename) as f:
        s = f.read()

    try:
        root = generate_xml(s)
    except ParserException as e:
        print('Error in {}:{}:'.format(filename, e.line))
        if hasattr(e.exception, 'lineno'):
            e.exception.filename = filename
            try:
                raise e.exception
            except:
                pass            
            traceback.print_exc(limit=0)
        else:
            print(e.exception)
        quit(1)

    indent(root)
    print(ET.tostring(root, encoding='utf-8').decode('utf-8'))
