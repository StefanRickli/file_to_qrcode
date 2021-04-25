import os
import base64

import treepoem

qr_code_eclevel = 'L'
chunk_size = 2000


def write_qr_code(file_path: str):
    file_basename = os.path.basename(file_path)

    f = open(file_basename, 'rb')
    data = f.read()
    f.close()

    data_b32txt = base64.b32encode(data).decode()
    chunks = [data_b32txt[i:i + chunk_size] for i in range(0, len(data_b32txt), chunk_size)]

    for i, qr_code_content in enumerate(chunks):
        image = treepoem.generate_barcode('qrcode', qr_code_content, {'eclevel': qr_code_eclevel})
        image.save(f'./assets/{file_basename}_{i}.png')


def run():
    # backup_code_file_path = './backup_to_qrcode.py'
    restore_code_file_path = './restore_from_scan.py'

    # write_qr_code(backup_code_file_path)
    write_qr_code(restore_code_file_path)


if __name__ == '__main__':
    run()
