from django.http import HttpResponse
from django.template.loader import render_to_string

from weasyprint import HTML, CSS
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64
from random import sample
from multiprocessing import Pool

MM_TO_PIXEL_RATIO = 3.78

def generate_image(paper_size, range_min, range_max, base_image_path, font):
    numbers = sample(range(range_min, range_max), 6)

    # Load image for adding text
    base_image = Image.open(base_image_path)
    draw = ImageDraw.Draw(base_image)

    # Add numbers to text
    base_coord_x = 70
    base_coord_y = 2560
    coord_x_increment = 204
    for number in numbers:
        text = str(number)
        text_width, text_height = draw.textsize(text, font=font)
        coord_x = base_coord_x - (text_width / 2)
        coord_y = base_coord_y - (text_height / 2)
        draw.text(
            (coord_x, coord_y),
            text,
            font=font,
            fill='#000'
        )
        base_coord_x += coord_x_increment

    # Resize image to reduce file size
    if paper_size == "a4":
        max_pixel_height = 267 * MM_TO_PIXEL_RATIO
    elif paper_size == "letter":
        max_pixel_height = 249 * MM_TO_PIXEL_RATIO
    (width, height) = base_image.size
    if height > max_pixel_height:
        ratio = max_pixel_height / height
        width *= ratio
        height *= ratio
        base_image = base_image.resize((int(width), int(height)), Image.ANTIALIAS)

    # Save image to buffer
    image_buffer = BytesIO()
    base_image.save(image_buffer, format='PNG')
    return base64.b64encode(image_buffer.getvalue())

class PageCreator(object):
    def __init__(self, paper_size, range_min, range_max, base_image_path, font_path, font_size):
        self.paper_size = paper_size
        self.range_min = range_min
        self.range_max = range_max
        self.base_image_path = base_image_path
        self.font_path = font_path
        self.font_size = font_size

    def __call__(self, call_num):
        font = ImageFont.truetype(self.font_path, self.font_size)
        return generate_image(self.paper_size, self.range_min, self.range_max, self.base_image_path, font)

def pdf(request, resource, **kwargs):
    context = dict()

    # Create numbers to add to image
    difficulty = request.GET['difficulty']
    if difficulty == 'easy':
        range_min = 1
        range_max = 10
        font_size = 150
    elif difficulty == 'medium':
        range_min = 10
        range_max = 100
        font_size = 120
    else:
        range_min = 100
        range_max = 1000
        font_size = 90

    # Create resource image
    base_image_path = 'resources/content/{}/sorting-network-colour.png'.format(resource.folder)
    font_path = 'resources/content/fonts/PatrickHand-Regular.ttf'
    paper_size = request.GET['size']
    with Pool() as pool:
        context['resource_images'] = pool.map(PageCreator(paper_size, range_min, range_max, base_image_path, font_path, font_size), range(0, int(request.GET['copies'])))

    # Write to PDF
    context['paper_size'] = paper_size
    context['resource'] = resource
    html_string = render_to_string('resources/base-resource-pdf.html', context)

    html = HTML(string=html_string)
    base_css = CSS(string=open('static/css/print-resource-pdf.css', encoding='UTF-8').read())
    pdf_file = html.write_pdf(stylesheets=[base_css]);

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="example.pdf"'
    return response
