# Standard library
import sys
import os
from datetime import datetime
import glob
import ntpath
import posixpath
from pathlib import Path
import math
import base64
import json
import hashlib
import logging
import uuid

# Other modules
import treepoem

# Own modules
import generate_pdf
from assets import code_revisioning


chunk_size = 400
qr_code_eclevel = 'M'  # all options are [L, M, Q, H]
out_folder = './backup/out'

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


file_list = glob.glob('./backup/in/*')
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

software_timestamp = code_revisioning.get_software_timestamp()

hash_object = hashlib.sha256(data)
data_sha256 = hash_object.hexdigest().upper()
data_b32txt = base64.b32encode(data).decode()
chunk_data_arr = [data_b32txt[i:i + chunk_size] for i in range(0, len(data_b32txt), chunk_size)]

chunks_total = len(chunk_data_arr) + 1  # +1 for the metadata chunk
n_digits = math.ceil(math.log10(chunks_total))
pad_fmt = f'0{n_digits}'
batch_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
batch_uuid = uuid.uuid4().hex.upper()


def write_qr_code(chunk_idx, chunk_content, out_file_path):
    qr_code_content = json.dumps(chunk_content)

    # Since JSON contains characters that are not in the QR code alphanumeric
    # charset, we replace these characters.
    charset_mapping = {'{': '$%%', '}': '%%$', '_': '-', '"': '*', '=': '.', ',': '$$%'}
    for k, v in charset_mapping.items():
        qr_code_content = qr_code_content.replace(k, v)

    image = treepoem.generate_barcode('qrcode', qr_code_content, {'eclevel': qr_code_eclevel})

    width, height = image.size
    modules = int((width - 2) / 4)
    version = int(((modules - 21) / 4) + 1)
    logging.info(f"Chunk {chunk_idx:{pad_fmt}} of {chunks_total:{pad_fmt}}, "
                 f'Content length: {len(qr_code_content)}, '
                 f'EC Level: {qr_code_eclevel}, '
                 f'Modules: {modules}'
                 f' ==> Version: {version}')

    image.save(out_file_path)


# ################
# Metadata Chunk #
# ################

batch_metadata = {'software_timestamp': software_timestamp,
                  'file_name': input_file_name,
                  'file_sha256': data_sha256,
                  'batch_timestamp': batch_timestamp,
                  'batch_id': batch_uuid,
                  'chunks_total': chunks_total
                  }

# In order to allow the QR code engine to choose alphanumeric mode,
# caps for all chars are needed.
#
# Refer to https://www.qrcode.com/en/about/version.html
# for an explanation of the capacity of a QR code with
# respect to ECL, mode and version.
batch_metadata_qr = {'SOFTWARE_TIMESTAMP': software_timestamp,
                     'FILE_NAME': input_file_name_b64txt,
                     'FILE_SHA256': data_sha256,
                     'BATCH_TIMESTAMP': batch_timestamp,
                     'BATCH_ID': batch_uuid,
                     'CHUNKS_TOTAL': f'{chunks_total:{pad_fmt}}',
                     'CHUNK_IDX': f'{1:{pad_fmt}}'
                     }

out_file_path = f'{out_folder}/{input_file_name} ({1:{pad_fmt}} Metadata).png'
write_qr_code(1, batch_metadata_qr, out_file_path)

image_files = []
image_files.append({'chunk_idx': '1', 'chunk_img_path': out_file_path})

# #############
# Data Chunks #
# #############

for i, chunk_data in enumerate(chunk_data_arr):
    i += 2
    chunk_content = {
        'BATCH_ID': batch_uuid,
        'CHUNK_IDX': f'{i:{pad_fmt}}',
        'DATA': chunk_data
    }

    out_file_path = f'{out_folder}/{input_file_name} ({i:{pad_fmt}} of {chunks_total:{pad_fmt}}).png'
    write_qr_code(i, chunk_content, out_file_path)

    image_files.append({'chunk_idx': i,
                        'chunk_img_path': out_file_path
                        })

# -----------------------------------------------------------------------------------

print('Generating PDF...')
in_data = {'meta': batch_metadata, 'image_files': image_files}
pdf_file_path = f'{out_folder}/{input_file_name}.pdf'
generate_pdf.run(in_data, pdf_file_path)
print(f'File written to "{pdf_file_path}".')
print('Done!')
