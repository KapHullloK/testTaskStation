import json
from pprint import pprint


def get_delta_json(config_path, patch_path, output_path):
    data_config = None
    data_patched = None

    with open(config_path, 'r', encoding='utf-8') as f:
        data_config = json.load(f)

    with open(patch_path, 'r', encoding='utf-8') as f:
        data_patched = json.load(f)

    res = {}

    deletions = []
    updates = []

    for k, v in data_config.items():
        if k not in data_patched:
            deletions.append(k)
        else:
            if data_config[k] != data_patched[k]:
                updates.append({
                    'key': k,
                    'from': data_config[k],
                    'to': data_patched[k],
                })

    deletions_set = set(deletions)

    adds = []
    for k, v in data_patched.items():
        if k not in data_config and k not in deletions_set:
            adds.append({
                'key': k,
                'value': v
            })

    res['additions'] = adds
    res['deletions'] = deletions
    res['updates'] = updates

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(res, f, indent=4, ensure_ascii=False)


def get_patched_json(delta_path, config_path, output_path):
    data_delta = None
    data_config = None

    with open(delta_path, 'r', encoding='utf-8') as f:
        data_delta = json.load(f)

    with open(config_path, 'r', encoding='utf-8') as f:
        data_config = json.load(f)

    for k in data_delta['deletions']:
        data_config.pop(k)

    for obj in data_delta['updates']:
        if obj['key'] in data_config:
            data_config[obj['key']] = obj['to']

    for obj in data_delta['additions']:
        data_config[obj['key']] = obj['value']

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data_config, f, indent=4, ensure_ascii=False)
