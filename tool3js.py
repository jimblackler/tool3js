import argparse
import base64
import hashlib
import json
import os


def main():
  parser = argparse.ArgumentParser(description='Processor for Three.js scene files.')
  parser.add_argument('input', help='Filename of file to process')
  parser.add_argument('--output', help='Filename to send output to')
  parser.add_argument('--urls', help='Output type of urls', choices=['data', 'file'])

  args = parser.parse_args()

  base = os.path.dirname(args.input)

  with open(args.input) as f:
    scene = json.load(f)

  hashes = {}
  if args.urls == 'file':
    for root, subdirs, files in os.walk(base):
      for filename in files:
        full_filename = os.path.join(root, filename)
        bytes_read = open(full_filename, 'rb').read()
        hashes[hashlib.sha256(bytes_read).hexdigest()] = os.path.relpath(full_filename, base)

  for image in scene['images']:
    if 'url' in image:
      url = image['url']
      if args.urls == 'data':
        with open(os.path.join(base, url), 'rb') as data:
          image['url'] = 'data:image/jpeg;base64,' + base64.b64encode(data.read())
      elif args.urls == 'file':
        parts = url.split(';base64,', 1)
        if len(parts) == 2:
          digest = hashlib.sha256(base64.b64decode(parts[1])).hexdigest()
          if digest in hashes:
            image['url'] = hashes[digest]

  with open(os.path.join(base, args.output), 'w') as f:
    json.dump(scene, f, indent=2)


if __name__ == "__main__":
  main()
