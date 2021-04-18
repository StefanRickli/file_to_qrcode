import sys
import os
import glob
import ntpath
import posixpath
from pathlib import Path
import math
import base64
import json
import hashlib
import treepoem
import logging
import generate_pdf
import uuid
import subprocess

# https://gist.github.com/ethanwhite/ba63849c26301f862e4e
process = subprocess.Popen(['git', 'rev-parse', 'HEAD'], shell=False, stdout=subprocess.PIPE)
git_head_hash = process.communicate()[0].strip().decode()[0:7]

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


file_list = glob.glob('./encode/in/*')
newest_file = max(file_list, key=os.path.getmtime)
print(f'Converting {newest_file} to QR codes')
if os.name == 'nt':
    input_file_path = ntpath.basename(newest_file)
else:
    input_file_path = posixpath.basename(newest_file)
input_file_name = Path(input_file_path).name
input_file_name_b64txt = base64.b32encode(input_file_name.encode()).decode()

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
batch_uuid = str(uuid.uuid4().hex).upper()
files = []
for i, chunk_data in enumerate(chunk_data_arr):
    # Caps for all chars are needed to allow the QR code
    # engine to choose alphanumeric mode.
    #
    # Refer to https://www.qrcode.com/en/about/version.html
    # for an explanation of the capacity of a QR code with
    # respect to ECL, mode and version.
    if i == 0:
        chunk = {
            'FILE_NAME': input_file_name_b64txt,
            'FILE_SHA256': data_hash,
            'CHUNK_IDX': f'{i+1:{pad_fmt}}',
            'CHUNKS_TOTAL': f'{chunks_total:{pad_fmt}}',
            'BATCH_UUID': batch_uuid,
            'GIT_REV': git_head_hash.upper(),
            'DATA': chunk_data
        }
    else:
        chunk = {
            'BATCH_UUID': batch_uuid,
            'CHUNK_IDX': f'{i+1:{pad_fmt}}',
            'DATA': chunk_data
        }

    code_content = json.dumps(chunk)

    # Custom character mapping to QR code alphanumeric charset allows
    # QR code generator to compress the data (see 'QR code mode').
    mapping = {'{': '$%%', '}': '%%$', '_': '-', '"': '*', '=': '.', ',': '$$%'}
    for k, v in mapping.items():
        code_content = code_content.replace(k, v)

    image = treepoem.generate_barcode('qrcode', code_content, {'eclevel': qr_code_eclevel})

    width, height = image.size
    modules = int((width - 2) / 4)
    version = int(((modules - 21) / 4) + 1)
    logging.info(f'Chunk {i+1:{pad_fmt}} of {chunks_total:{pad_fmt}}, Content length: {len(code_content)}, EC Level: {qr_code_eclevel}, Modules: {modules} ==> Version: {version}')

    out_file_path = f'{out_folder}/{input_file_name} ({i+1:{pad_fmt}} of {chunks_total:{pad_fmt}}).png'
    image.save(out_file_path)

    files.append({'file_name': input_file_name, 'file_sha256': data_hash, 'git_hash': git_head_hash, 'chunk_img': out_file_path, 'chunk_idx': i+1, 'chunk_total': chunks_total})

print('Generating PDF...')
pdf_file_path = f'{out_folder}/{input_file_name}.pdf'
generate_pdf.run(files, pdf_file_path)
print(f'File written to "{pdf_file_path}".')
print('Done!')
