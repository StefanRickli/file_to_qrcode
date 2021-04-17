import sys
import os
import glob

file_list = glob.glob('./decode/in/*.txt')
newest_file = max(file_list, key=os.path.getctime)

try:
    f = open(newest_file, 'r')
except Exception as e:
    print(e)
    sys.exit(1)

raw = f.read()
f.close()

data_dict = {}

chunks = raw.replace('\n', '').split('|')
for chunk in chunks:
    if '?' in chunk and ':' in chunk:
        filename, chunk_rest = chunk.split('?')
        chunk_number, chunk_data = chunk_rest.split(':')
        print(filename, chunk_number)
        data_dict[f'{filename}_{chunk_number}'] = chunk_data

keys = sorted(data_dict.keys())
data = [data_dict[k] for k in keys]
txt = ''.join(data)

f = open(f'./decode/out/{filename}', 'w')
f.write(txt)
f.close()
