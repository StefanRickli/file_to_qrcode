import os
import glob
# import argparse
# from qrtools import qrtools
# from reportlab.pdfgen import canvas
from reportlab.platypus import PageBreak, FrameBreak, Paragraph, Image, Spacer, NextPageTemplate
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from assets.reportlab_classes import qr_code_doc_template

page_width, page_height = A4


def run(files, out_file, frame_border=0):
    story = []

    # FirstPage Template is already active and will draw its stuff before the PageBreak
    story.append(NextPageTemplate('ContentPage'))
    story.append(PageBreak())

    for i, f in enumerate(files):
        story.append(Paragraph(f"Chunk {f['chunk_idx']} / {f['chunk_total']}"))
        story.append(Spacer(width=0, height=5 * mm))
        img_dim = page_width/2 - 50 * mm
        story.append(Image(f['chunk_img'], width=img_dim, height=img_dim, hAlign='LEFT'))
        story.append(FrameBreak())

    doc = qr_code_doc_template(out_file, files[0]['file_name'], files[0]['file_sha256'], files[0]['git_commit_unixtime'], frame_border=frame_border, pagesize=A4)
    doc.multiBuild(story)


if __name__ == '__main__':
    files = [{'file_name': 'test_file.txt', 'file_sha256': 'D3F3C5CD377CA1690D1D99352C7AEEC7551B00CFDEDFC42F43E43D9EFAE6E816', 'git_hash': 'D453AEF9', 'chunk_img': p, 'chunk_idx': i+1, 'chunk_total': 27} for i, p in enumerate(glob.glob('./encode/out/*.png'))]  # fix name, index one-indexing
    experiment_number = 0
    while True:
        out_file = f'./test/{experiment_number:03}.pdf'
        if os.path.exists(out_file):
            experiment_number += 1
        else:
            break

    run(files, out_file, frame_border=1)
    os.system("start " + os.path.abspath(out_file))
