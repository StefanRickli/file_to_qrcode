from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame
from reportlab.pdfgen.canvas import Canvas
from assets.test_qrcode_generator import get_test_qrcode

page_width, page_height = A4

page_margin_top = 25 * mm
page_margin_bottom = 20 * mm
page_margin_left = 17 * mm  # to avoid punches
page_margin_right = 10 * mm
page_footer_text_y = 10 * mm

frame_padding_top = 7 * mm
frame_padding_left = 5 * mm
frame_padding_right = 5 * mm


# https://stackoverflow.com/a/59882495/2721597
class NumberedPageCanvas(Canvas):
    """
    http://code.activestate.com/recipes/546511-page-x-of-y-with-reportlab/
    http://code.activestate.com/recipes/576832/
    http://www.blog.pythonlibrary.org/2013/08/12/reportlab-how-to-add-page-numbers/
    """

    def __init__(self, *args, **kwargs):
        """Constructor"""
        super().__init__(*args, **kwargs)
        self.pages = []

    def showPage(self):
        """
        On a page break, add information to the list
        """
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """
        Add the page number to each page (page x of y)
        """
        page_count = len(self.pages)

        for page in self.pages:
            self.__dict__.update(page)
            self.draw_page_number(page_count)
            super().showPage()

        super().save()

    def draw_page_number(self, page_count):
        """
        Add the page number
        """
        page = "Page %s of %s" % (self._pageNumber, page_count)
        self.drawRightString(page_width - page_margin_right, page_footer_text_y, page)


class qr_code_doc_template(BaseDocTemplate):
    def __init__(self, in_metadata, out_file_path, frame_border=0, **kw):
        super().__init__(out_file_path, **kw)
        self.software_timestamp = in_metadata['software_timestamp']
        self.file_name = in_metadata['file_name']
        self.file_sha256 = in_metadata['file_sha256']
        self.batch_timestamp = in_metadata['batch_timestamp']

        self.topMargin = page_margin_top
        self.bottomMargin = page_margin_bottom
        self.leftMargin = page_margin_left
        self.rightMargin = page_margin_right

        self.frameBorder = frame_border

        self.prepare_page_templates()

    def prepare_page_templates(self):
        first_page_template = PageTemplate('FirstPage', Frame(self.leftMargin,
                                                              self.bottomMargin,
                                                              page_width - self.rightMargin,
                                                              page_height - self.topMargin,
                                                              id='FirstPageFrame'), onPage=self.draw_first_page)

        frame_width = (page_width - self.leftMargin - self.rightMargin) / 2
        frame_height = (page_height - self.topMargin - self.bottomMargin) / 3
        frames = [
            Frame(self.leftMargin,                  self.bottomMargin + 2 * frame_height,   frame_width,   frame_height,    topPadding=frame_padding_top,   leftPadding=frame_padding_left, rightPadding=frame_padding_right,   id='F11', showBoundary=self.frameBorder),  # noqa: E241,E501
            Frame(self.leftMargin + frame_width,    self.bottomMargin + 2 * frame_height,   frame_width,   frame_height,    topPadding=frame_padding_top,   leftPadding=frame_padding_left, rightPadding=frame_padding_right,   id='F12', showBoundary=self.frameBorder),  # noqa: E241,E501
            Frame(self.leftMargin,                  self.bottomMargin + frame_height,       frame_width,   frame_height,    topPadding=frame_padding_top,   leftPadding=frame_padding_left, rightPadding=frame_padding_right,   id='F21', showBoundary=self.frameBorder),  # noqa: E241,E501
            Frame(self.leftMargin + frame_width,    self.bottomMargin + frame_height,       frame_width,   frame_height,    topPadding=frame_padding_top,   leftPadding=frame_padding_left, rightPadding=frame_padding_right,   id='F22', showBoundary=self.frameBorder),  # noqa: E241,E501
            Frame(self.leftMargin,                  self.bottomMargin,                      frame_width,   frame_height,    topPadding=frame_padding_top,   leftPadding=frame_padding_left, rightPadding=frame_padding_right,   id='F31', showBoundary=self.frameBorder),  # noqa: E241,E501
            Frame(self.leftMargin + frame_width,    self.bottomMargin,                      frame_width,   frame_height,    topPadding=frame_padding_top,   leftPadding=frame_padding_left, rightPadding=frame_padding_right,   id='F32', showBoundary=self.frameBorder),  # noqa: E241,E501
        ]
        content_page_template = PageTemplate('ContentPage', frames, onPage=self.draw_common_elements)
        self.addPageTemplates([first_page_template, content_page_template])

    def draw_first_page(self, canvas, doc):
        test_string, test_qrcode = get_test_qrcode()

        canvas.saveState()
        canvas.setFont("Helvetica-Bold", 24)
        canvas.drawCentredString(page_width / 2, page_height - 50 * mm, self.file_name)
        canvas.setFont("Helvetica", 12)
        canvas.drawCentredString(page_width / 2, page_height - 60 * mm, f'Generated: {self.batch_timestamp}')
        canvas.drawCentredString(page_width / 2, page_height - 70 * mm, 'Source Code: https://github.com/StefanRickli/file_to_qrcode')    # noqa: E241,E501
        canvas.drawCentredString(page_width / 2, page_height - 75 * mm, f'Software Timestamp: {self.software_timestamp}')                 # noqa: E241,E501
        canvas.setFont("Helvetica", 10)
        canvas.drawString(self.leftMargin, self.bottomMargin + 3 * 5 * mm, 'Please make sure that your 2D scanner correctly reproduces')  # noqa: E241,E501
        canvas.drawString(self.leftMargin, self.bottomMargin + 2 * 5 * mm, 'the string below when scanning the QR code to the right.')    # noqa: E241,E501
        canvas.drawString(self.leftMargin, self.bottomMargin + 1 * 5 * mm, 'Pay special attention to X/Y and the symbols.')               # noqa: E241,E501
        canvas.drawString(self.leftMargin, self.bottomMargin + 0 * 5 * mm, test_string)
        canvas.drawInlineImage(test_qrcode, x=125 * mm, y=self.bottomMargin - 1 * mm, width=19 * mm, height=19 * mm)
        canvas.restoreState()

    def draw_common_elements(self, canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 12)
        canvas.drawString(page_margin_left, page_height - 15 * mm, 'File Name:')
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(page_margin_left + 25 * mm, page_height - 15 * mm, f'{self.file_name}')
        canvas.setFont("Helvetica", 12)
        canvas.drawString(page_margin_left, page_height - 20 * mm, 'SHA256:')
        canvas.setFont("Helvetica", 10)
        canvas.drawString(page_margin_left + 25 * mm, page_height - 20 * mm, f'{self.file_sha256.lower()}')
        canvas.setFont("Helvetica", 12)
        canvas.drawString(page_margin_left, page_footer_text_y, self.batch_timestamp)
        canvas.restoreState()

    def build(self, flowables, filename=None, canvasmaker=NumberedPageCanvas):
        super().build(flowables, filename, canvasmaker)
