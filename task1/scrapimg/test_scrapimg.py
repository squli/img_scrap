import sys
import unittest
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from pathlib import Path
import shutil
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from scrapimg import fetch_url, ScrapImg


def get_referense(url):
    if urlparse(url).scheme == "":
        url = "https://" + url
    response = fetch_url(url)
    soup = BeautifulSoup(response.text, features="html.parser")
    images = soup.findAll('img')
    return len(images)


class TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in Path.cwd().iterdir():
            if item.is_dir():
                if "scrap_img_" in item.name or "wrong_url_" in item.name:
                    shutil.rmtree(item)  # Remove directory and its contents

    def test_scrap_webpage(self):
        urls = ["https://varjo.com/products/xr-4-secure-edition/",  # large images, srcsets, lazy images
                "http://www.nortfort.ru/hameenlinna/index_e/",  # http, old-fashion static webpage
                "https://www.yle.fi/a/74-20112293",  # all sorts of possible formats
                "https://yle.fi/a/74-20112293",
                "www.yle.fi/a/74-20112293",
                "yle.fi/a/74-20112293",
                "https://dopiaza.org/tools/datauri/examples/index.php",  # page with two data:image
                "https://www.espoo.fi/fi",
                "https://shinka.website.yandexcloud.net/",  # it has images in css files
                "https://www.google.com/search?sca_esv=6d171d08af1b8f7f&sca_upv=1&sxsrf=ADLYWIKXN1z5OFv"
                "-x44g89swChFigIcgZQ:1726694713764&q=forest&udm=2&fbs"
                "=AEQNm0BGIGwLWEDSb1sf9biXUg7SagJX9HKRAVtInHuMfoF_mWlKEWuo3cVP8ds"
                "-NUlgBJdwjx5pkM7C0wS5feQOQFTZV7ugykVSiruMyS-JrysCclIAwJFoEasrIqY0zKV2FqnK1MRKdvh1g-GDjF"
                "-BOBTygumyiFiVwP_DUjmIjemy26t4AxyTiXVJcmBr0aBXtHEKQ6G8EcKJZzE0HbI1FYbms7K5nQ&sa=X&ved"
                "=2ahUKEwiYsbKIt82IAxVeExAIHcQFBh8QtKgLegQIEhAB&biw=1745&bih=866&dpr=1.1"]  # bad filenames for images

        i = 0
        for url in urls:
            print(f"Download from {url[:64]} to scrap_img_{i}")
            scrap_img = ScrapImg(url_=url, folder_path=f"scrap_img_{i}")
            reference_amount = get_referense(url)
            scrap_img._prepare_folder()
            scrap_img_amount, css_files_amount = scrap_img.get_images_links()
            self.assertEqual(reference_amount, scrap_img_amount, "Reference img count doesn't equal calculated")
            files_count = scrap_img.download_images()
            self.assertEqual(files_count, len(scrap_img.image_links))
            print(scrap_img)
            i += 1

    def test_wrong_url_webpage(self):
        urls = ["httpsjhsfkurfujdks", "http://fdgdfgdfgdfg"]
        i = 0
        for u in urls:
            scrap_img = ScrapImg(url_=u, folder_path=f"wrong_url_{i}")
            self.assertRaises(ScrapImg.UrlFetchingError, scrap_img.scrap_images)
            i += 1


if __name__ == '__main__':
    unittest.main()
