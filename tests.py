import unittest

from pdf2image import convert_from_path
from pdf2image.exceptions import PDFPageCountError

from utils.algorithms import get_zone_region


class Test(unittest.TestCase):

    def pdf_to_png_ok(self):
        images = convert_from_path('data/forms/01/001/01/01/Mesa 001.pdf')
        self.assertEqual(1, len(images))

    def pdf_to_png_path_not_found(self):
        self.assertRaises(PDFPageCountError, convert_from_path, 'data/Mesa.pdf')

    def pdf_to_png_not_args(self):
        self.assertRaises(TypeError, convert_from_path)

    def get_zone_region(self):
        images = convert_from_path('data/forms/01/001/01/01/Mesa 001.pdf')
        image = images[0].convert('RGB')
        zone_region = get_zone_region(image)


if __name__ == '__main__':
    unittest.main()
