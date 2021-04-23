import os
import glob
from reportlab.platypus import PageBreak, FrameBreak, Paragraph, Image, Spacer, NextPageTemplate
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from assets.reportlab_classes import qr_code_doc_template

page_width, page_height = A4


def run(in_data, out_file_path, frame_border=0):
    story = []

    # FirstPage Template is already active and will draw its stuff before the PageBreak
    story.append(NextPageTemplate('ContentPage'))
    story.append(PageBreak())

    files = in_data['image_files']
    for f in files:
        story.append(Paragraph(f"Chunk {f['chunk_idx']} / {in_data['meta']['chunks_total']}"))
        story.append(Spacer(width=0, height=5 * mm))
        img_dim = (page_width / 2) - 50 * mm
        story.append(Image(f['chunk_img_path'], width=img_dim, height=img_dim, hAlign='LEFT'))
        story.append(FrameBreak())

    doc = qr_code_doc_template(in_metadata=in_data['meta'],
                               out_file_path=out_file_path,
                               frame_border=frame_border,
                               pagesize=A4)
    doc.multiBuild(story)


if __name__ == '__main__':
    files = glob.glob('./backup/out/*.png')
    batch_metadata = {'software_timestamp': 'Timestamp here',
                      'file_name': 'example_file.txt',
                      'file_sha256': 'SHA256 here',
                      'batch_timestamp': 'Timestamp here',
                      'batch_id': 'UUID here',
                      'chunks_total': len(files)
                      }
    image_files = [{'chunk_idx': i + 1,
                    'chunk_img_path': p} for i, p in enumerate(files)]
    in_data = {'meta': batch_metadata, 'image_files': image_files}

    experiment_number = 0
    while True:
        out_file_path = f'./test/{experiment_number:03}.pdf'
        if os.path.exists(out_file_path):
            experiment_number += 1
        else:
            break

    run(in_data, out_file_path, frame_border=1)
    os.system("start " + os.path.abspath(out_file_path))
