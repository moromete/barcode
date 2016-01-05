import os
import sys
import shutil

def main():
  indir = sys.argv[1]
  outdir = sys.argv[2]
  
  if not os.path.exists(outdir):
    os.makedirs(outdir)
  
  for root, dirs, filenames in os.walk(indir):
    for f in filenames:
      print(f)
      shutil.copyfile(os.path.join(indir,f), os.path.join(outdir, f));
      
main()
        