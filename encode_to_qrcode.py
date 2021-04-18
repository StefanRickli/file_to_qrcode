import sys
import os
import glob, ntpath, posixpath
import math
import base64
import json
import hashlib
import treepoem
import logging
import generate_pdf

chunk_size = 400
qr_code_eclevel = 'M'  # all options are [L, M, Q, H]
out_folder = './encode/out'

experiment_number = 0
while True:
    log_filename = f'{out_folder}/{experiment_number:03}.log'
    if os.path.exists(log_filename):
        experiment_number += 1
    else:
        break

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)


file_list = glob.glob('./encode/in/*.txt')
newest_file = max(file_list, key=os.path.getmtime)
print(f'Converting {newest_file} to QR codes')
if os.name == 'nt':
    newest_file_name = ntpath.basename(newest_file)
else:
    newest_file_name = posixpath.basename(newest_file)
file_name_b64txt = base64.b32encode(newest_file_name.encode()).decode()

try:
    f = open(newest_file, 'rb')
except Exception as e:
    print(e)
    sys.exit(1)

data = f.read()
f.close()

hash_object = hashlib.sha256(data)
data_hash = hash_object.hexdigest().upper()
data_b64txt = base64.b32encode(data).decode()
chunk_data_arr = [data_b64txt[i:i+chunk_size] for i in range(0, len(data_b64txt), chunk_size)]

chunks_total = len(chunk_data_arr)
n_digits = math.ceil(math.log10(chunks_total))
pad_fmt = f'0{n_digits}'
files = []
for i, chunk_data in enumerate(chunk_data_arr):
    chunk = {
        # 'file_name': f'{file_name_b64txt}',
        # 'file_sha256': data_hash,
        # 'chunk_idx': f'{i+1:{pad_fmt}}',
        # 'chunk_total': f'{chunks_total:{pad_fmt}}',
        # 'data': chunk_data
        'FILE_NAME': f'{file_name_b64txt}',
        'FILE_SHA256': data_hash,
        'CHUNK_IDX': f'{i+1:{pad_fmt}}',
        'CHUNKS_TOTAL': f'{chunks_total:{pad_fmt}}',
        'DATA': chunk_data
    }

    code_content = json.dumps(chunk)

    # Custom character mapping to QR code alphanumeric charset allows
    # QR code generator to compress the data (see 'QR code mode')
    mapping = {'{': '$%%', '}': '%%$', '_': '-', '"': '*', '=': '.', ',': '$$%'}
    for k, v in mapping.items():
        code_content = code_content.replace(k, v)

    image = treepoem.generate_barcode('qrcode', code_content, {'eclevel': qr_code_eclevel})

    width, height = image.size
    modules = (width - 2) / 4
    version = ((modules - 21) / 4) + 1
    logging.info(f'ECL: {qr_code_eclevel}, Length: {len(code_content)}, Modules: {modules}, Version: {version}')

    out_filename = f'{out_folder}/{newest_file_name} ({i+1:{pad_fmt}} of {chunks_total:{pad_fmt}}).png'
    print(out_filename)
    image.save(out_filename)

    files.append({'file_name': newest_file_name, 'file_sha256': data_hash, 'chunk_img': out_filename, 'chunk_idx': i+1, 'chunk_total': chunks_total})

print('Generating PDF...')
pdf_file = f'{out_folder}/{newest_file_name}.pdf'
generate_pdf.run(files, pdf_file)
print('Done!')
