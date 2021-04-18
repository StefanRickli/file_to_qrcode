import sys
import os
import glob, ntpath, posixpath
import math
import base64
import json
import hashlib
import treepoem

chunk_size = 400
qr_code_eclevel = 'Q'  # all options are [L, M, Q, H]

file_list = glob.glob('./encode/in/*.txt')
newest_file = max(file_list, key=os.path.getmtime)
print(f'Converting {newest_file} to QR codes')
if os.name == 'nt':
    newest_file_name = ntpath.basename(newest_file)
else:
    newest_file_name = posixpath.basename(newest_file)
file_name_b64txt = base64.b64encode(newest_file_name.encode()).decode()

try:
    f = open(newest_file, 'rb')
except Exception as e:
    print(e)
    sys.exit(1)

data = f.read()
f.close()

hash_object = hashlib.sha256(data)
data_hash = hash_object.hexdigest()
data_b64txt = base64.b64encode(data).decode()
chunk_data_arr = [data_b64txt[i:i+chunk_size] for i in range(0, len(data_b64txt), chunk_size)]

chunks_total = len(chunk_data_arr)
n_digits = math.ceil(chunks_total/10)
pad_fmt = f'0{n_digits}'
for i, chunk_data in enumerate(chunk_data_arr):
    chunk = {
        'file_name': f'{file_name_b64txt}',
        'file_sha256': data_hash,
        'chunk_idx': f'{i+1:{pad_fmt}}',
        'chunks_total': f'{chunks_total:{pad_fmt}}',
        'data': chunk_data
    }

    code_content = json.dumps(chunk)

    # Custom character mapping to QR code alphanumeric charset allows
    # QR code generator to compress the data (see 'QR code mode')
    mapping = {'{': '$%%', '}': '%%$', '_': '-', '"': '*', '=': '.', ',': '$$%'}
    for k, v in mapping.items():
        code_content = code_content.replace(k, v)

    image = treepoem.generate_barcode('qrcode', code_content, {'eclevel': qr_code_eclevel})
    out_filename = f'./encode/out/{newest_file_name} ({i+1:{pad_fmt}} of {chunks_total:{pad_fmt}}).png'
    print(out_filename)
    image.save(out_filename)
