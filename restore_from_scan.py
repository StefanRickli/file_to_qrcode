import sys
import os
import json
import base64
import hashlib
import argparse
import logging

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--source', type=str, required=True)
parser.add_argument('-d', '--destination', type=str,
                    help='Can be either a file or folder.')
parser.add_argument('-l', '--logfile', type=str)
args = parser.parse_args()

if not os.path.isfile(args.source):
    raise ValueError(f'Source file does not exist: "{args.source}"')

in_file_path = args.source
in_file_name = os.path.split(in_file_path)[1]
in_file_basename = os.path.basename(in_file_path)
in_folder = os.path.dirname(in_file_path)

if args.destination is None:
    out_folder = in_folder
    out_file_basename = in_file_basename
else:
    dest_path = args.destination
    if os.path.basename(dest_path):
        # File given
        out_file_path = dest_path
        out_file_basename = os.path.basename(dest_path)
        out_folder = os.path.dirname(dest_path)
    else:
        # Folder given
        out_file_path = os.path.join(out_folder, in_file_name)
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

logger.info(f'Stitching together "{in_file_path}"')

# No error handling at the moment since we want to quit if for any reason we can't read the file
try:
    f = open(in_file_path, 'r')
    raw = f.read()
    f.close()
except Exception as e:
    logger.info(e)
    sys.exit(1)

got_header = False
chunk_data_arr = {}
chunk_numbers = set()
batch_ids = []

code_contents = raw.splitlines()
for i, code_content in enumerate(code_contents):
    try:
        # First, revert custom character mapping (QR code optimization, see 'QR code mode')
        mapping = {'$%%': '{', '%%$': '}', '-': '_', '*': '"', '.': '=', '$$%': ','}
        for k, v in mapping.items():
            code_content = code_content.replace(k, v)

        chunk = json.loads(code_content)

        if int(chunk['CHUNK_IDX']) == 1:
            got_header = True
            software_timestamp = chunk['SOFTWARE_TIMESTAMP']
            orig_file_name = base64.b32decode(chunk['FILE_NAME'].encode()).decode()
            orig_file_sha256 = chunk['FILE_SHA256'].lower()
            batch_timestamp = chunk['BATCH_TIMESTAMP']
            batch_uuid = chunk['BATCH_ID'].lower()
            chunks_total = int(chunk['CHUNKS_TOTAL'])

            logger.info(f"Original file name: {orig_file_name}")
            logger.info(f"Original file hash (SHA256):  {orig_file_sha256}")
            logger.info(f"Total chunks to process: {chunks_total}")
        else:
            chunk_data_arr[f"{chunk['BATCH_ID']}_{chunk['CHUNK_IDX']}"] = chunk['DATA']

        batch_ids.append(chunk['BATCH_ID'].lower())
        chunk_numbers.add(int(chunk['CHUNK_IDX']))

        logger.info(f"Found chunk #{chunk['CHUNK_IDX']}")

    except json.JSONDecodeError:
        pass

if not got_header:
    raise ValueError('Missing first chunk (containting metadata)')

all_chunk_numbers = set(range(1, chunks_total + 1))
chunks_not_seen = all_chunk_numbers - chunk_numbers
if chunks_not_seen:
    raise ValueError(f'Missing the following chunks: {chunks_not_seen}')

if not all(chunk_batch_id == batch_uuid for chunk_batch_id in batch_ids):
    raise ValueError('Batch ID mismatch: at least one chunk stems from different generation pass')

keys = sorted(chunk_data_arr.keys())
chunk_data_sorted = [chunk_data_arr[k] for k in keys]
data_b32txt = ''.join(chunk_data_sorted)
data = base64.b32decode(data_b32txt.encode())

hash_object = hashlib.sha256(data)
data_hash = hash_object.hexdigest()
logger.info(f'Decoded data hash: {data_hash}')
if data_hash != orig_file_sha256:
    raise ValueError('Decoded data hash does not match with original hash')
logger.info('Hashes match.')

out_file = os.path.join(out_folder, orig_file_name)
f = open(f'{out_file}', 'wb')
f.write(data)
f.close()

logger.info(f'Restored file to "{out_file}"')
