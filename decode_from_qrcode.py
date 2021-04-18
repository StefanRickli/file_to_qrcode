import sys, traceback
import os
import glob
import json
import base64
import hashlib

in_folder = './decode/in'
out_folder = './decode/out'

file_list = glob.glob(f'{in_folder}/*.txt')
try:
    newest_file = max(file_list, key=os.path.getmtime)
except ValueError:
    print(f'Could not find a file to process in "{in_folder}"')
    sys.exit(1)
print(f'Stitching together "{newest_file}"')

try:
    f = open(newest_file, 'r')
except Exception as e:
    traceback.print_exc()
    sys.exit(1)

raw = f.read()
f.close()

got_chunk = False
chunk_data_arr = {}
chunk_numbers = []

code_contents = raw.splitlines()
for i, code_content in enumerate(code_contents):
    # print(code_content)
    try:
        chunk = json.loads(code_content)
        if got_chunk:
            if file_name != chunk['file_name']:
                raise ValueError('File name mismatch')
            if file_hash != chunk['file_sha256']:
                raise ValueError('File hash mismatch')
            if chunks_total != int(chunk['chunks_total']):
                raise ValueError('Chunk total mismatch')
        else:
            got_chunk = True
            print(f"Original file name: {chunk['file_name']}")
            print(f"Original file hash (SHA256):  {chunk['file_sha256']}")
            print(f"Total chunks to process: {chunk['chunks_total']}")
            file_name = chunk['file_name']
            file_hash = chunk['file_sha256']
            chunks_total = int(chunk['chunks_total'])
        
        print(f"Found chunk #{chunk['chunk_idx']}")

        chunk_data_arr[f"{chunk['file_name']}_{chunk['chunk_idx']}"] = chunk['data']
        chunk_numbers.append(int(chunk['chunk_idx']))
    except json.JSONDecodeError as e:
        pass

if not all(i in chunk_numbers for i in range(1, chunks_total+1)):
    raise ValueError('Missing at least one chunk')

keys = sorted(chunk_data_arr.keys())
chunk_data_sorted = [chunk_data_arr[k] for k in keys]
data_b64txt = ''.join(chunk_data_sorted)
data = base64.b64decode(data_b64txt.encode())

hash_object = hashlib.sha256(data)
data_hash = hash_object.hexdigest()
print(f'Decoded data hash: {data_hash}')
if data_hash != file_hash:
    raise ValueError('Decoded data hash does not match with original hash')
print('Hashes match.')

out_file = os.path.join(out_folder, file_name)
f = open(f'{out_file}', 'wb')
f.write(data)
f.close()

print(f'Restored file to "{out_file}"')
