# Standard library
import sys
import os
from datetime import datetime
import math
import base64
import json
import hashlib
import logging
import uuid
import argparse

# Other modules
import treepoem

# Own modules
import generate_pdf
from assets import code_revisioning


# -----------------------------------------------------------------------------------

def write_qr_code(chunk_idx, chunk_content, out_file_path, qr_code_eclevel):
    qr_code_content = json.dumps(chunk_content)

    # Since JSON contains characters that are not in the QR code alphanumeric
    # charset, we replace these characters.
    charset_mapping = {'{': '$%%', '}': '%%$', '_': '-', '"': '*', '=': '.', ',': '$$%'}
    for k, v in charset_mapping.items():
        qr_code_content = qr_code_content.replace(k, v)

    if args.verbose:
        verbose_logger.info(qr_code_content)

    image = treepoem.generate_barcode('qrcode', qr_code_content, {'eclevel': qr_code_eclevel})

    width, height = image.size
    modules = int((width - 2) / 4)
    version = int(((modules - 21) / 4) + 1)
    logger.info(f"Chunk {chunk_idx:{pad_fmt}} of {chunks_total:{pad_fmt}}, "
                f'Content length: {len(qr_code_content)}, '
                f'EC Level: {qr_code_eclevel}, '
                f'Modules: {modules}'
                f' ==> Version: {version}')

    image.save(out_file_path)


# -----------------------------------------------------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--source', type=str, required=True)
parser.add_argument('-d', '--destination', type=str, required=True,
                    help='Can be either a PDF file or a folder. '
                    'In case of folder, only QR code PNG files are created.')
parser.add_argument('-l', '--logfile', type=str)
parser.add_argument('--chunk_size', type=int, default=400,
                    help='Sets the size of the data chunks in # of characters. '
                         'Note that this does not inlcude the chunk header.')
parser.add_argument('--qr_code_eclevel', type=str, default='M',
                    help='Determines the error correction level of the QR code. '
                         'Valid arguments are "L", "M", "Q", "H".')
parser.add_argument('--preserve_tempfiles', action='store_true',
                    help='If destination is a PDF file, this flag will prevent '
                    'the temporary image files to be deleted.')
parser.add_argument('-v', '--verbose', action='store_true',
                    help='Generate text file containing QR code contents.')

args = parser.parse_args()

if not os.path.isfile(args.source):
    raise ValueError(f'Source file does not exist: "{args.source}"')

in_file_path = args.source
in_file_basename = os.path.basename(in_file_path)

dest_path = args.destination
if os.path.basename(dest_path):
    out_file_extension = os.path.splitext(args.destination)[1]
    if out_file_extension != '.pdf':
        raise ValueError(f'Unknown destination file extension: "{out_file_extension}". Need ".pdf" or ".PDF".')
    run_pdf_generation = True
    out_file_path = dest_path
    out_file_basename = os.path.basename(dest_path)
    out_folder = os.path.dirname(dest_path)
else:
    run_pdf_generation = False
    out_file_path = dest_path
    out_file_basename = in_file_basename
    out_folder = dest_path

if args.logfile is None:
    log_file_path = f'{os.path.join(out_folder, out_file_basename)}.log'
else:
    if not os.path.basename(args.logfile):
        raise ValueError(f'Logfile path is not target to a file: "{args.logfile}"')
    log_file_path = args.logfile

formatter = logging.Formatter('%(message)s')
logger = logging.getLogger('Regular logger')
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(log_file_path, mode='w')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler(stream=sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

if args.qr_code_eclevel not in ['L', 'M', 'Q', 'H']:
    raise ValueError(f'Unexpected value for "qr_code_eclevel": {args.qr_code_eclevel}')

if args.verbose:
    verbose_formatter = logging.Formatter('%(message)s')
    verbose_logger = logging.getLogger('Verbose Logger')
    verbose_logger.setLevel(logging.DEBUG)

    verbose_file_path = f'{os.path.join(out_folder, out_file_basename)}.qr.txt'
    verbose_handler = logging.FileHandler(verbose_file_path, mode='w')
    verbose_handler.setFormatter(verbose_formatter)
    verbose_logger.addHandler(verbose_handler)

logger.info(f'Converting "{in_file_path}" to "{out_folder}"')

# -----------------------------------------------------------------------------------

# #################
# Read input file #
# #################

try:
    f = open(in_file_path, 'rb')
    data = f.read()
    f.close()
except Exception as e:
    logger.info(e)
    sys.exit(1)

# ######################
# Assemble (meta-)data #
# ######################

software_timestamp = code_revisioning.get_software_timestamp()

in_file_basename_b32txt = base64.b32encode(in_file_basename.encode()).decode()

data_sha256 = hashlib.sha256(data).hexdigest().upper()
data_b32txt = base64.b32encode(data).decode()
chunk_data_arr = [data_b32txt[i:i + args.chunk_size] for i in range(0, len(data_b32txt), args.chunk_size)]

chunks_total = len(chunk_data_arr) + 1  # +1 for the metadata chunk
n_digits = math.floor(math.log10(chunks_total)) + 1
pad_fmt = f'0{n_digits}'
batch_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
batch_uuid = uuid.uuid4().hex.upper()

# ################
# Metadata Chunk #
# ################

batch_metadata = {'software_timestamp': software_timestamp,
                  'file_name': in_file_basename,
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
                     'FILE_NAME': in_file_basename_b32txt,
                     'FILE_SHA256': data_sha256,
                     'BATCH_TIMESTAMP': batch_timestamp,
                     'BATCH_ID': batch_uuid,
                     'CHUNKS_TOTAL': f'{chunks_total:{pad_fmt}}',
                     'CHUNK_IDX': f'{1:{pad_fmt}}'
                     }

img_file_path = f'{out_folder}/{in_file_basename} ({1:{pad_fmt}} Metadata).png'
write_qr_code(1, batch_metadata_qr, img_file_path, args.qr_code_eclevel)

image_files = []
image_files.append({'chunk_idx': '1', 'chunk_img_path': img_file_path})

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

    img_file_path = f'{out_folder}/{out_file_basename} ({i:{pad_fmt}} of {chunks_total:{pad_fmt}}).png'
    write_qr_code(i, chunk_content, img_file_path, args.qr_code_eclevel)

    image_files.append({'chunk_idx': i,
                        'chunk_img_path': img_file_path
                        })

# -----------------------------------------------------------------------------------

if run_pdf_generation:
    logger.info('Generating PDF...')
    in_data = {'meta': batch_metadata, 'image_files': image_files}
    generate_pdf.run(in_data, out_file_path)
    logger.info(f'PDF file written to "{out_file_path}".')
    logger.info('Done!')

if not args.preserve_tempfiles:
    for image_file in image_files:
        os.remove(image_file['chunk_img_path'])
