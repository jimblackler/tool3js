import argparse
import base64
import json
import os


def data_url_from(filename):
  with open(filename, 'rb') as data:
    return 'data:image/jpeg;base64,' + base64.b64encode(data.read())


def main():
  parser = argparse.ArgumentParser(description='Processor for Three.js scene files.')
  parser.add_argument('input', help='Filename of file to process')
  parser.add_argument('--output', help='Filename to send output to')
  parser.add_argument('--urls', help='Output type of urls', choices=['data', 'file'])

  args = parser.parse_args()

  with open(args.input) as file:
    scene = json.load(file)

  for image in scene['images']:
    if 'url' in image:
      url = image['url']
      if args.urls == 'data':
        image['url'] = data_url_from(os.path.join(os.path.dirname(args.input), url))

  with open(os.path.join(os.path.dirname(args.input), args.output), 'w') as file:
    json.dump(scene, file, indent=2)


if __name__ == "__main__":
  main()
