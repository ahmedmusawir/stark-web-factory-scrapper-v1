"""Shared Q2 reference scanner.

Collects every {file, sha256}-shaped reference from a prepared-package JSON
index: any dict key named "file" or ending in "_file" is treated as a
reference, with its sibling hash key ("sha256" for "file", "<prefix>_sha256"
for "<prefix>_file") and optional sibling byte-count key. The count derived
here is independent of any documented package figure.
"""


def find_file_references(obj, prefix="$"):
    refs = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if (k == "file" or k.endswith("_file")) and isinstance(v, str):
                sha_key = "sha256" if k == "file" else k[:-5] + "_sha256"
                bytes_key = "bytes" if k == "file" else k[:-5] + "_bytes"
                refs.append({
                    "json_path": prefix + "." + k,
                    "file": v,
                    "sha256": obj.get(sha_key),
                    "bytes": obj.get(bytes_key),
                })
        for k, v in obj.items():
            refs.extend(find_file_references(v, prefix + "." + k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            refs.extend(find_file_references(v, prefix + "[%d]" % i))
    return refs