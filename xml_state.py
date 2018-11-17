import xml.etree.ElementTree as ET


def _count(values):
    if type(values) == list or type(values) == tuple:
        return len(values)
    elif values is None:
        return 0
    else:
        return 1


def _stringify(values):
    if type(values) == list or type(values) == tuple:
        return " ".join([str(x) for x in values])
    elif type(values) == type(True):
        return "1" if values else "0"
    else:
        return str(values)


class XMLNode(ET.Element):
    def __init__(self, tag=None, attrib={}, parent=None):
        if tag is None:
            tag = 'ServerManagerConfiguration'
        ET.Element.__init__(self, tag, attrib)
        self.parent = parent        
        if self.parent is not None:
            self.parent.append(self)
        self.context = {}

    def _find_group(self, name):
        if self.tag == 'ServerManagerConfiguration':
            child = self.find('./ProxyGroup[@name="{}"]'.format(name))
            if child is not None:
                return child
            return XMLNode('ProxyGroup', {'name': name}, self)
        elif self.parent is None:
            raise Exception('No XML root.')
        else:
            return self.parent._find_group(name)

    def _get_hints(self):
        hints = self.find('./Hints')
        if hints is None:
            hints = XMLNode('Hints', {}, self)
        return hints

    def _find_source(self):
        if self.tag == 'SourceProxy':
            return self
        elif self.parent is None:
            raise Exception('No source proxy.')
        else:
            return self.parent._find_source()
        return root

    def source(self, name=None, label=None, class_=None, group='sources'):
        root = self._find_group(group)
        d = { 'name': name, 'label': label, 'class': class_}
        try:
            if d['class'] is None:
                d['class'] = self.context['class']
            if d['name'] is None:
                d['name'] = self.context.get('name', d['class'])
            if d['label'] is None:
                d['label'] = self.context.get('label', d['name'])                
        except KeyError as e:
            raise Exception('Missing parameter: {}'.format(e.args[0]))

        return XMLNode('SourceProxy', d, root)

    def filter(self, name=None, label=None, class_=None):
        return self.source(name, label, class_, group='filters')

    def _vector(self, type_=None, name=None, label=None, 
                command=None, command_prefix='Set', group_id=None,
                number_of_elements=None, default_values=None):
        root = self._find_source()

        d = { 
          'name': name, 
          'label': label,
          'command': command,
          'number_of_elements': number_of_elements,
          'default_values': default_values,
        }
        try:
            if type_ is None:
                type_ = self.context['type']
            if d['name'] is None:
                d['name'] = self.context['name']
            if d['label'] is None:
                d['label'] = self.context.get('label', d['name'])
            if d['command'] is None:
                d['command'] = self.context.get('command', command_prefix + d['name'])
            if d['default_values'] is None:
                d['default_values'] = self.context['default_values']
            if d['number_of_elements'] is None:
                d['number_of_elements'] = self.context.get('number_of_elements', _count(d['default_values']))
        except KeyError as e:
            raise Exception('Missing parameter: {}'.format(e.args[0]))

        d['default_values'] = _stringify(d['default_values'])
        d['number_of_elements'] = _stringify(d['number_of_elements'])

        if type_ == 'int' or type_ == 'bool':
            xml_type = 'Int'
        elif type_ == 'double' or type_ == 'float':
            xml_type = 'Double'
        else:
            raise Exception('Invalid vector property type: {}'.format(type_))        

        node = XMLNode('{}VectorProperty'.format(xml_type), d, root)
        node.group_id = group_id
        return node.boolean() if type_ == 'bool' else node

    def intvector(self, **kwargs):
        return self._vector(type_='int', **kwargs)

    def doublevector(self, *args, **kwargs):
        return self._vector(type_='double', **kwargs)

    def autovector(self, *args, **kwargs):
        return self._vector(**kwargs)

    def enumeration(self, items, values):
        if self.tag != 'IntVectorProperty':
            raise Exception('"enumeration" cannot be added to "{}"'.format(self.tag))
        if len(items) != len(values):
            raise Exception('items and values must be of same length')
        domain = XMLNode('EnumerationDomain', { 'name': 'enum' }, self)
        for value, text in zip(values, items):
            XMLNode('Entry', { 'value': _stringify(value), 'text': _stringify(text) }, domain)
        return self

    def boolean(self, *args, **kwargs):
        if self.tag != 'IntVectorProperty':
            raise Exception('"boolean" cannot be added to "{}"'.format(self.tag))
        XMLNode('BooleanDomain', { 'name': 'bool' }, self)
        return self
    
    def menu(self, category):
        XMLNode('ShowInMenu', { 'category': category }, self._find_source()._get_hints())
        return self

    def replace_input(self, mode):
        XMLNode('Visibility', { 'replace_input': _stringify(mode) }, self._find_source()._get_hints())
        return self        

    def group(self, label, group_id):
        root = self._find_source()

        node = XMLNode('PropertyGroup', { 'label': label }, root)
        for child in root:
            if hasattr(child, 'group_id') and child.group_id == group_id:
                XMLNode('Property', { 'name': child.attrib['name'] }, node)

        return node

    def widget_visibility(self, property_, value):
        if self.tag != 'PropertyGroup' and not self.tag.endswith('VectorProperty'):
            raise Exception('"widget_visibility" cannot be added to "{}"'.format(self.tag))

        d = {
          'type': 'GenericDecorator',
          'mode': 'visibility',
          'property': _stringify(property_),
          'value': _stringify(value),
        }
        XMLNode('PropertyWidgetDecorator', d, self._get_hints())
        return self

    def xml(self, xml_string):
        self.append(ET.fromstring(xml_string))
        return self

    def xml_hint(self, xml_string):
        root = self
        if root.tag not in ['PropertyGroup', 'SourceProxy'] and not root.tag.endswith('VectorProperty'):
            root = self.parent
        if root is None or root.tag not in ['PropertyGroup', 'SourceProxy'] and not root.tag.endswith('VectorProperty'):
            raise Exception('hint cannot be added to "{}"'.format(self.tag))

        self._get_hints().append(ET.fromstring(xml_string))
        return self
