"""Optional: re-download exactly the public dataset used in this project."""
from pathlib import Path
import hashlib
import json
import urllib.request

ROOT = Path(__file__).resolve().parent


def main():
    manifest = json.loads((ROOT / 'data/provenance.json').read_text(encoding='utf-8'))
    payload = urllib.request.urlopen(manifest['source_url'], timeout=60).read()
    if hashlib.sha256(payload).hexdigest() != manifest['sha256']:
        raise ValueError('Downloaded data do not match the pinned checksum')
    (ROOT / 'data/tan2009_rep1.csv').write_bytes(payload)
    print('Verified and saved data/tan2009_rep1.csv')


if __name__ == '__main__':
    main()
