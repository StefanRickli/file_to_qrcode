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
    for i, f in enumerate(files):
        story.append(Paragraph(f"Chunk {f['chunk_idx']} / {f['chunk_total']}"))
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
    file_metadata = {'file_name': 'test_file.txt',
                     'file_sha256': 'D3F3C5CD377CA1690D1D99352C7AEEC7551B00CFDEDFC42F43E43D9EFAE6E816',
                     'software_timestamp': '2021-04-22 18:30:01'}
    image_files = [{'chunk_idx': i + 1,
                    'chunk_total': 27,
                    'chunk_img_path': p} for i, p in enumerate(glob.glob('./backup/out/*.png'))]
    in_data = {'meta': file_metadata, 'image_files': image_files}

    experiment_number = 0
    while True:
        out_file_path = f'./test/{experiment_number:03}.pdf'
        if os.path.exists(out_file_path):
            experiment_number += 1
        else:
            break

    run(in_data, out_file_path, frame_border=1)
    os.system("start " + os.path.abspath(out_file_path))
