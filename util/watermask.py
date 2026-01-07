from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color


class WatermarkCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startNewPage()

    def save(self):
        """Vẽ watermark TRƯỚC khi lưu trang (rất quan trọng!)"""
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_watermark()
        canvas.Canvas.save(self)

    def draw_watermark(self):
        self.saveState()

        text = "HocCode.io"  # Thay nội dung tuỳ ý
        font_size = 90
        angle = -45
        opacity = 0.12  # Mờ vừa đủ, đẹp
        spacing = 500  # Khoảng cách rộng → không bị chồng

        # Dùng font tiếng Việt bạn đã register
        try:
            self.setFont("DejaVu-Bold", font_size)
        except:
            self.setFont("Helvetica-Bold", font_size)

        # Set độ trong suốt (hoạt động trên mọi phiên bản ReportLab >= 3.4)
        try:
            self.setFillAlpha(opacity)
        except AttributeError:
            self.setFillColor(Color(180, 180, 180, alpha=opacity))

        width, height = A4

        self.translate(width / 2, height / 2)
        self.rotate(angle)

        # Vẽ lưới đều, đẹp, không chồng lấn
        for x in range(-1500, 1500, spacing):
            for y in range(-2000, 2000, spacing):
                self.drawCentredString(x, y, text)

        self.restoreState()
