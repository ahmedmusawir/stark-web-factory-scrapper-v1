"""C6 minimal read-only raw reader. Invalid raw is refused, valid partial accepted."""
import argparse
import hashlib
from pathlib import Path

from smart_crawler.validate import InvalidRaw, load, reference, validate_run


class RawRun:
    def __init__(self, root):
        self.root=Path(root).resolve()
        self.checks=validate_run(self.root)
        self.manifest=load(self.root/'manifest.json')
        self.absences=load(self.root/'absences.json')
        self.routes=load(self.root/'discovery/routes.json')
        self.rest_index=load(self.root/'rest/index.json')
        self.rest_map=load(self.root/'rest/map.json')
        self.media=load(self.root/'media/inventory.json')

    def bytes(self, ref, owner='manifest.json'):
        return reference(self.root,owner,ref).read_bytes()

    def json(self, ref, owner='manifest.json'):
        return load(reference(self.root,owner,ref))

    def inventory(self):
        return {p.relative_to(self.root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(self.root.rglob('*')) if p.is_file()}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw',type=Path,required=True)
    args=parser.parse_args()
    try:
        raw=RawRun(args.raw)
        print(f"VALID RAW: {len(raw.manifest['pages'])} route outcomes; Prepare construction is a separate stage")
    except InvalidRaw as exc:
        print('PREPARE REFUSED: '+str(exc))
        raise SystemExit(3)


if __name__=='__main__':main()
