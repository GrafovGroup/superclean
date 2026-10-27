"""Optimize one original image and persist its provenance for resumable generation."""
from pathlib import Path
from PIL import Image
import json, sys

root = Path(__file__).resolve().parent.parent
name, source = sys.argv[1:3]
assert all(c.isalnum() or c == '-' for c in name)
destination = root / 'public/assets/photos/cities' / (name + '.webp')
destination.parent.mkdir(parents=True, exist_ok=True)
image = Image.open(source).convert('RGB')
image.thumbnail((1000, 750))
image.save(destination, 'WEBP', quality=80, method=6)
record = {'key': name, 'image': '/assets/photos/cities/' + name + '.webp', 'source_file': Path(source).name, 'width': image.width, 'height': image.height, 'bytes': destination.stat().st_size, 'origin': 'original AI-generated illustrative service photograph; not a documented client project'}
with (root / 'content/city-image-provenance.jsonl').open('a') as out:
    out.write(json.dumps(record) + '\n')
print(json.dumps(record))
