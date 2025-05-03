from compare_jsons import get_delta_json, get_patched_json
from xml_worker import XMLWorker

if __name__ == '__main__':
    f = XMLWorker('impulse_test_input.xml')
    folder = 'out/'
    f.generate_config(folder + 'config.xml')
    f.generate_json(folder + 'meta.json')

    get_delta_json('config.json', 'patched_config.json', folder + 'delta.json')
    get_patched_json(folder + 'delta.json', 'config.json', folder + 'res_patched_config.json')
