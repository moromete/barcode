import os
#import sys
import shutil
import argparse

import zbar
#import Image
from PIL import Image

total = 0
renamed = 0
skipped = 0

def main():
  global total, renamed, skipped
  
  parser = argparse.ArgumentParser()
  parser.add_argument("indir", help="source directory")
  parser.add_argument("outdir", help="destination directory")
  parser.add_argument("-m", "--move", help="delete files from source directory after rename",
                      action="store_true")
  args = parser.parse_args()
  
  indir = args.indir
  outdir = args.outdir
    
  if not os.path.exists(outdir):
    os.makedirs(outdir)
  
  for root, dirs, filenames in os.walk(indir):
    print 'PARSE FILES ...'
    print '--------------------------'
    for f in filenames:
      total = total+1
      print f
      code = scan(os.path.join(indir, f))
      if (code != None) :
        renamed = renamed+1
        extension = os.path.splitext(f)[1]
        if args.move:
          shutil.move(os.path.join(indir,f), os.path.join(outdir, (code + '.'+extension)))
        else:
          shutil.copyfile(os.path.join(indir,f), os.path.join(outdir, (code + '.'+extension)))
      else:
        skipped = skipped+1
        print 'BAR CODE NOT FOUND !!!'
      print '--------------------------'
  
  print 'total = ', total, ' renamed = ', renamed, ' skipped = ', skipped

def scan(img):
  # create a reader
  scanner = zbar.ImageScanner()
  
  # configure the reader
  scanner.parse_config('enable')
  
  # obtain image data
  pil = Image.open(img).convert('L')
  width, height = pil.size
  raw = pil.tostring()
  
  # wrap image data
  image = zbar.Image(width, height, 'Y800', raw)
  
  # scan the image for barcodes
  scanner.scan(image)
  
  # extract results
  code = None
  for symbol in image:
    # do something useful with results
    print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data
    code = symbol.data
    break

  # clean up
  del(image)
  return code

############################################################################      

main()
