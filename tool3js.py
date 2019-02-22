import argparse
import base64
import hashlib
import json
import mimetypes
import os


def main():
  parser = argparse.ArgumentParser(description='Processor for Three.js scene files.')
  parser.add_argument('input', help='Filename of file to process')
  parser.add_argument('--output', help='Filename to send output to (defaults to same as imput)')
  parser.add_argument('--assets', help='Relative folder for created assets')
  parser.add_argument('--urls', help='Output type of urls', choices=['data', 'file'])

  args = parser.parse_args()

  base = os.path.dirname(args.output or args.input)

  with open(args.input) as f:
    scene = json.load(f)

  hashes = {}
  if args.urls == 'file':
    for root, _, files in os.walk(base):
      for filename in files:
        full_filename = os.path.join(root, filename)
        bytes_read = open(full_filename, 'rb').read()
        hashes[hashlib.sha256(bytes_read).hexdigest()] = os.path.relpath(full_filename, base)

  replaced = 0
  for image in scene['images']:
    if 'url' in image:
      url = image['url']
      if args.urls == 'data':
        if url.startswith('data:'):
          continue
        with open(os.path.join(base, url), 'rb') as data:
          image['url'] = 'data:' + mimetypes.guess_type(url)[0] + ';base64,' + base64.b64encode(data.read())
          replaced += 1
      elif args.urls == 'file':
        parts = url.split(';base64,', 1)
        if len(parts) != 2:
          continue
        data = base64.b64decode(parts[1])
        digest = hashlib.sha256(data).hexdigest()
        if digest not in hashes:
          mime_type = parts[0].split('data:', 1)[1]
          asset_filename = os.path.join(args.assets or '', image['uuid'] + mimetypes.guess_extension(mime_type))
          print 'Creating %s' % asset_filename
          with open(os.path.join(base, asset_filename), 'wb') as f:
            f.write(data)
          image['url'] = asset_filename
        else:
          image['url'] = hashes[digest]
        replaced += 1

  print 'Replaced %d images' % replaced
  with open(os.path.join(base, args.output or args.input), 'w') as f:
    json.dump(scene, f, indent=2)


if __name__ == "__main__":
  main()
