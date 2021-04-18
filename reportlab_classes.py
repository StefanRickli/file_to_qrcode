from datetime import datetime
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame
from reportlab.pdfgen.canvas import Canvas

page_width, page_height = A4
page_margin_top = 25 * mm
page_margin_bottom = 20 * mm
page_margin_left = 17 * mm  # to avoid punches
page_margin_right = 10 * mm
page_footer_text_y = 10 * mm
frame_padding_top = 10 * mm
frame_padding_left = 5 * mm
frame_padding_right = 5 * mm
frame_border = 0  # either 0 or 1


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
    def __init__(self, out_file, file_name, file_sha256, **kw):
        super().__init__(out_file, **kw)
        self.file_name = file_name
        self.file_sha256 = file_sha256
        self.generation_timestamp = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")

        self.topMargin = page_margin_top
        self.bottomMargin = page_margin_bottom
        self.leftMargin = page_margin_left
        self.rightMargin = page_margin_right

        frame_width = (page_width - self.leftMargin - self.rightMargin) / 2
        frame_height = (page_height - self.topMargin - self.bottomMargin) / 2
        frames = [
            Frame(self.leftMargin,                  self.bottomMargin + frame_height,   frame_width,   frame_height,    topPadding=frame_padding_top,   leftPadding=frame_padding_left, rightPadding=frame_padding_right,     id='F11', showBoundary=frame_border),
            Frame(self.leftMargin + frame_width,    self.bottomMargin + frame_height,   frame_width,   frame_height,    topPadding=frame_padding_top,   leftPadding=frame_padding_left, rightPadding=frame_padding_right,    id='F12', showBoundary=frame_border),
            Frame(self.leftMargin,                  self.bottomMargin,                  frame_width,   frame_height,    topPadding=frame_padding_top,   leftPadding=frame_padding_left, rightPadding=frame_padding_right,    id='F21', showBoundary=frame_border),
            Frame(self.leftMargin + frame_width,    self.bottomMargin,                  frame_width,   frame_height,    topPadding=frame_padding_top,   leftPadding=frame_padding_left, rightPadding=frame_padding_right,    id='F22', showBoundary=frame_border),
        ]
        template = PageTemplate('normal', frames, onPage=self.draw_common_elements)
        self.addPageTemplates(template)

    def draw_common_elements(self, canvas, doc):
        canvas.saveState()
        canvas.drawString(page_margin_left, page_height - 15 * mm, f'File Name: {self.file_name}')
        canvas.drawString(page_margin_left, page_height - 20 * mm, f'SHA256: {self.file_sha256.lower()}')
        canvas.drawString(page_margin_left, page_footer_text_y, self.generation_timestamp)
        canvas.restoreState()

    def build(self, flowables, filename=None, canvasmaker=NumberedPageCanvas):
        super().build(flowables, filename, canvasmaker)
