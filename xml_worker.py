import json
import xml.etree.ElementTree as ET


class XMLWorker:

    def __init__(self, input_xml_path):
        self.input_xml_path = input_xml_path
        self.params = {}
        self.aggregations = {}
        self.fields = {}

        self.__get_all_info()

    def __get_all_info(self):
        tree = ET.parse(self.input_xml_path)
        root = tree.getroot()

        root_class = None

        for elem in root:
            if elem.tag == 'Class':
                name = elem.attrib['name']
                self.fields[name] = elem.attrib

                if elem.attrib['isRoot'] == 'true':
                    root_class = name

                attributes = []
                for child in elem:
                    if child.tag == 'Attribute':
                        attributes.append({
                            child.attrib['name']: child.attrib['type']
                        })
                self.params[name] = attributes
            elif elem.tag == 'Aggregation':
                val = elem.attrib['sourceMultiplicity'].split('..')

                if len(val) == 2:
                    self.fields[elem.attrib['source']]['max'] = val[1]
                    self.fields[elem.attrib['source']]['min'] = val[0]
                else:
                    self.fields[elem.attrib['source']]['max'] = val[0]
                    self.fields[elem.attrib['source']]['min'] = val[0]

                if self.aggregations.get(elem.attrib['target']):
                    self.aggregations[elem.attrib['target']].append(elem.attrib['source'])
                else:
                    self.aggregations[elem.attrib['target']] = [elem.attrib['source']]

        self.root_class = root_class

    def generate_config(self, output_path):

        def build_element(class_name):
            element = ET.Element(class_name)

            for attr_dict in self.params.get(class_name, []):
                for attr_name, attr_type in attr_dict.items():
                    sub = ET.SubElement(element, attr_name)
                    sub.text = attr_type

            for child_class in self.aggregations.get(class_name, []):
                child_element = build_element(child_class)
                element.append(child_element)

            return element

        config_root = build_element(self.root_class)
        config_tree = ET.ElementTree(config_root)

        config_tree.write(output_path, encoding='utf-8')

    def generate_json(self, output_path):
        res = []

        for name, info in self.fields.items():
            obj = {
                'class': name,
                'documentation': info.get('documentation', ''),
                'isRoot': info.get('isRoot') == 'true',
            }

            if self.fields[name].get('min'):
                obj['max'] = info.get('max')
                obj['min'] = info.get('min')

            obj['parameters'] = []

            for attr in self.params.get(name, []):
                for attr_name, attr_type in attr.items():
                    obj['parameters'].append({
                        'name': attr_name,
                        'type': attr_type
                    })

            for child in self.aggregations.get(name, []):
                obj['parameters'].append({
                    'name': child,
                    'type': 'class'
                })

            res.append(obj)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(res, f, indent=4, ensure_ascii=False)
