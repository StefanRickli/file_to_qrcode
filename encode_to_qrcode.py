import sys
import os
import glob, ntpath, posixpath
import treepoem

chunk_size = 180

file_list = glob.glob('./encode/in/*.txt')
newest_file = max(file_list, key=os.path.getctime)
if os.name == 'nt':
    newest_file_name = ntpath.basename(newest_file)
else:
    newest_file_name = posixpath.basename(newest_file)

try:
    f = open(newest_file, 'r')
except Exception as e:
    print(e)
    sys.exit(1)

data = f.read()
f.close()

chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]

for i, chunk in enumerate(chunks):
    image = treepoem.generate_barcode('qrcode', f'{newest_file_name}?{i:02}:' + chunk + '|', {})
    image.save(f'./encode/out/{newest_file_name} ({i:02}).png')
