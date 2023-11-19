#!/usr/bin/python

import json
import re
from os import chmod
from hashlib import md5
from pathlib import Path
from urllib.request import urlopen
from ansible.module_utils.basic import AnsibleModule


def fetch_release_info(project: str, tag: str) -> dict:
  with urlopen(f'https://api.github.com/repos/{project}/releases/' + (f'tags/{tag}' if tag != 'latest' else tag)) as res:
    if res.status != 200:
      raise Exception(f'got invalid status code: {res.status}')

    return json.loads(res.read().decode('utf8'))


def download_asset(asset: dict, dest: Path) -> str:
  with urlopen(asset['browser_download_url']) as res:
    if res.status != 200:
      raise Exception(f'got invalid status code: {res.status}')

    data = res.read()
    with dest.open(mode='wb') as f:
      f.write(data)

    return md5(data).hexdigest()


def main():
  args = {
      'project': {'required': True, 'type': 'str'},
      'tag': {'default': 'latest', 'type': 'str'},
      'match_asset': {'default': '', 'type': 'str'},
      'dest': {'required': True, 'type': 'str'},
      'mode': {'default': '644', 'type': 'str'}
  }

  module = AnsibleModule(argument_spec=args)

  release_info = fetch_release_info(module.params['project'], module.params['tag'])

  asset_matches = [asset for asset in release_info['assets']
                   if not module.params['match_asset'] or
                   re.match(module.params['match_asset'], asset['name']) is not None]

  if len(asset_matches) > 1:
    names = ','.join([asset['name'] for asset in asset_matches])
    module.fail_json(msg=f'found multiple asset matches: {names}')
  elif len(asset_matches) == 0:
    module.fail_json(msg=f'found no asset matches')

  out_file = Path(module.params['dest'])
  if out_file.is_dir():
    out_file = Path(out_file) / asset_matches[0]['name']

  result = {
      'changed': False,
      'dest': str(out_file.absolute()),
      'meta': module.params
  }

  before_checksum = None
  if out_file.exists():
    with out_file.open(mode='rb') as f:
      before_checksum = md5(f.read()).hexdigest()

  after_checksum = download_asset(asset_matches[0], out_file)
  chmod(out_file, int(module.params['mode'], 8))

  result['changed'] = before_checksum is None or before_checksum != after_checksum
  module.exit_json(**result)


if __name__ == '__main__':
  main()
