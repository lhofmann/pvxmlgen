import xml.etree.ElementTree as ET


def _count(values):
    if type(values) == list or type(values) == tuple:
        return len(values)
    elif values is None:
        return 0
    else:
        return 1


def _stringify(values):
    if isinstance(values, list) or isinstance(values, tuple):
        return ' '.join([str(x) for x in values])
    elif isinstance(values, type(True)):
        return '1' if values else '0'
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

    # ------------------------------------------------------------------------------
    # source proxies
    # ------------------------------------------------------------------------------

    def source(self, name=None, label=None, class_=None, group='sources'):
        root = self._find_group(group)
        d = {'name': name, 'label': label, 'class': class_}
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

    # ------------------------------------------------------------------------------
    # properties
    # ------------------------------------------------------------------------------

    def input(self, data_types, name='Input', label='Input', port_index=0, multiple_input=False):
        root = self._find_source()
        d = {
            'name': name,
            'label': label,
            'port_index': _stringify(port_index),
        }
        if multiple_input:
            d['command'] = 'AddInputConnection'
            d['clean_command'] = 'RemoveAllInputs'
        else:
            d['command'] = 'SetInputConnection'

        node = XMLNode('InputProperty', d, root)

        domain = XMLNode('DataTypeDomain', {'name': 'input_type'}, node)
        if type(data_types) != list and type(data_types) != tuple:
            data_types = [data_types]
        for dtype in data_types:
            XMLNode('DataType', {'value': dtype}, domain)

        return node

    def input_array(self, label, idx=0, input_domain_name='input_array', input_name='Input',
                    none_string=None, attribute_type=None, data_type=None):
        root = self._find_source()

        d_prop = {
            'name': 'SelectInputScalars{}'.format(idx),
            'label': label,
            'command': 'SetInputArrayToProcess',
            'default_values': _stringify(idx),
            'element_types': '0 0 0 0 2',
            'animateable': '0'
        }

        node = XMLNode('StringVectorProperty', d_prop, root)

        d_array = {
            'name': 'array_list',
            'input_domain_name': input_domain_name,
        }
        if attribute_type is not None:
            if attribute_type not in ['Scalars', 'Vectors']:
                raise Exception('Invalid attribute_type')
            d_array['attribute_type'] = attribute_type
        if none_string is not None:
            d_array['none_string'] = none_string
        if data_type is not None:
            if data_type[:4] != 'VTK_':
                raise Exception('data_type must name a VTK_ type')
            d_array['data_type'] = data_type

        array_list = XMLNode('ArrayListDomain', d_array, node)
        req = XMLNode('RequiredProperties', {}, array_list)
        XMLNode('Property', {'name': input_name, 'function': 'Input'}, req)

        field_data = XMLNode('FieldDataDomain', {'name': 'field_list'}, node)
        req = XMLNode('RequiredProperties', {}, field_data)
        XMLNode('Property', {'name': input_name, 'function': 'Input'}, req)

        return node

    def _vector(self, type_=None, name=None, label=None,
                command=None, command_prefix='Set', group_id=None,
                number_of_elements=None, default_values=None, animateable=None,
                panel_visibility=None):
        root = self._find_source()

        d = {
            'name': name,
            'label': label,
            'command': command,
            'number_of_elements': number_of_elements,
            'default_values': default_values,
        }
        if animateable is not None:
            d['animateable'] = _stringify(animateable)
        if panel_visibility is not None:
            if panel_visibility not in ['default', 'never', 'advanced']:
                raise Exception('Invalid value for panel_visibility')
            d['panel_visibility'] = panel_visibility
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

    def group(self, label, group_id):
        root = self._find_source()

        node = XMLNode('PropertyGroup', {'label': label}, root)
        for child in root:
            if hasattr(child, 'group_id') and child.group_id == group_id:
                XMLNode('Property', {'name': child.attrib['name']}, node)

        return node

    # ------------------------------------------------------------------------------
    # property domains
    # ------------------------------------------------------------------------------

    def array_domain(self, name='input_array', attribute_type='any', number_of_components=None, optional=None):
        if self.tag != 'InputProperty':
            raise Exception('"input_array" cannot be added to "{}"'.format(self.tag))
        if attribute_type not in ['point', 'cell', 'any', 'row']:
            raise Exception('Invalid attribute_type "{}"'.format(attribute_type))
        d = {
            'name': name,
            'attribute_type': attribute_type
        }
        if number_of_components is not None:
            d['number_of_components'] = _stringify(number_of_components)
        if optional is not None:
            d['optional'] = _stringify(optional)

        XMLNode('InputArrayDomain', d, self)
        return self

    def enumeration(self, items, values):
        if self.tag != 'IntVectorProperty':
            raise Exception('"enumeration" cannot be added to "{}"'.format(self.tag))
        if len(items) != len(values):
            raise Exception('items and values must be of same length')
        domain = XMLNode('EnumerationDomain', {'name': 'enum'}, self)
        for value, text in zip(values, items):
            XMLNode('Entry', {'value': _stringify(value), 'text': _stringify(text)}, domain)
        return self

    def boolean(self, *args, **kwargs):
        if self.tag != 'IntVectorProperty':
            raise Exception('"boolean" cannot be added to "{}"'.format(self.tag))
        XMLNode('BooleanDomain', {'name': 'bool'}, self)
        return self

    def range(self, min, max):
        if self.tag == 'IntVectorProperty':
            tag = 'IntRangeDomain'
        elif self.tag == 'DoubleVectorProperty':
            tag = 'DoubleRangeDomain'
        else:
            raise Exception('"range" cannot be added to "{}"'.format(self.tag))
        d = {
            'name': 'range',
            'min': _stringify(min),
            'max': _stringify(max),
        }
        XMLNode(tag, d, self)
        return self

    # ------------------------------------------------------------------------------
    # hints
    # ------------------------------------------------------------------------------

    def menu(self, category):
        XMLNode('ShowInMenu', {'category': category}, self._find_source()._get_hints())
        return self

    def replace_input(self, mode):
        XMLNode('Visibility', {'replace_input': _stringify(mode)}, self._find_source()._get_hints())
        return self

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

    def documentation(self, text=None, short_help=None, long_help=None):
        d = {}
        if short_help is not None:
            d['short_help'] = short_help
        if long_help is not None:
            d['long_help'] = long_help
        node = XMLNode('Documentation', d, self)
        if text is not None:
            node.text = text
        return self

    # ------------------------------------------------------------------------------
    # raw XML methods
    # ------------------------------------------------------------------------------

    def xml(self, xml_string):
        self.append(ET.fromstring(xml_string))
        return self

    def xml_property(self, xml_string):
        root = self._find_source()
        root.append(ET.fromstring(xml_string))
        return root

    def xml_hint(self, xml_string):
        root = self
        if root.tag not in ['PropertyGroup', 'SourceProxy'] and not root.tag.endswith('VectorProperty'):
            root = self.parent
        if root is None or root.tag not in ['PropertyGroup', 'SourceProxy'] and not root.tag.endswith('VectorProperty'):
            raise Exception('hint cannot be added to "{}"'.format(self.tag))

        root._get_hints().append(ET.fromstring(xml_string))
        return root
