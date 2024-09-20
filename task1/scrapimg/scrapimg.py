import time
import zlib
import requests
import shutil
import base64
import re
from pathlib import Path
from html.parser import HTMLParser
from threading import Thread
from urllib.parse import urlparse, urljoin


class ImgTagAndCssParser(HTMLParser):
    def __init__(self, base_url):
        super().__init__()
        self.img_tags = []
        self.css_links = []
        self.base_url = base_url

    def error(self, message):
        raise ValueError

    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            img_attributes = {}
            for attr, value in attrs:
                img_attributes[attr] = value
            self.img_tags.append(img_attributes)
        elif tag == 'link':
            attr_dict = dict(attrs)
            if attr_dict.get('rel') == 'stylesheet' and 'href' in attr_dict:
                full_url = urljoin(self.base_url, attr_dict['href'])
                self.css_links.append(full_url)


def sanitize_name(folder_name: str) -> str:
    # folder names do not allow certain characters: \ / : * ? " < > |
    valid_chars = re.compile(r'[^\w\s-]')
    sanitized_name = valid_chars.sub('', folder_name)
    return sanitized_name.strip()


def fetch_url(url_to_fetch: str):
    fake_headers = {
        "Accept": "*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) "
                      "Version/15.4 Safari/605.1.15",
        "Accept-Encoding": "*",
        "Accept-Language": "*",
        "Cache-Control": "max-age=2592000,immutable",
        "Connection": "keep-alive"
    }
    try:
        response = requests.get(url_to_fetch, headers=fake_headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        raise ScrapImg.UrlFetchingError(f"Exception {e} for url={url_to_fetch}")
    return response


class ScrapImg:
    DEFAULT_FOLDER_NAME = "images"
    MAX_FILENAME_LEN = 64

    class UrlFetchingError(Exception):
        def __init__(self, value):
            self.value = value

        def __str__(self):
            return repr(self.value)

    def __init__(self, url_: str, folder_path: str = None):
        if urlparse(url_).scheme == "":
            url_ = "https://" + url_
        self.url = url_
        self.domain = urlparse(self.url).netloc
        self.scheme = urlparse(self.url).scheme
        if folder_path:
            self.path = Path(folder_path)
        else:
            self.path = Path(Path.cwd() / ScrapImg.DEFAULT_FOLDER_NAME)
        self.image_links = []

    def _prepare_folder(self):
        if self.path.exists():
            shutil.rmtree(self.path)
        self.path.mkdir(parents=True)

    def _prepare_css_links(self, css_links):
        """
        Append to list of image links image files from the css files
        :param css_links: list with links to css files
        :return:
        """

        def get_images_from_css(css_link: str, css_file_contents: str):
            url_pattern = r'url\((.*?)\)'
            urls = re.findall(url_pattern, css_file_contents)
            images_urls = [url_.strip('\'"') for url_ in urls]
            css_images = []
            for img_url in images_urls:
                if Path(img_url).suffix in image_exts:
                    css_images.append(urljoin(css_link, img_url))
            return css_images

        image_exts = [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".tif"]
        links = []
        for link in css_links:
            response = fetch_url(link)
            links += get_images_from_css(link, response.text)
            #print(f"In {link} found {links}")

        [self.image_links.append(item) for item in links if item not in self.image_links]
        return

    def _prepare_image_links(self, img_tags):
        """
        Append links to list of image links from attributes of the img tag
        :param img_tags: list of records from html parser with img-tags
        :return:
        """

        def prepare_link(input_link: str, scheme: str = self.scheme, domain: str = self.domain):
            if "data:image" in input_link:
                return input_link
            image_src = urlparse(input_link).netloc
            if not image_src:
                return f"{scheme}://{domain}{input_link}"
            return input_link

        def split_srcset(srcset: str):
            pattern = re.compile(r'[^,\s]+(?:,[^,\s]+)?(?:\s+\d+\w*)?')
            matches = pattern.findall(srcset)
            return map(lambda string: string.split(" ")[0], matches)

        links = []
        for link in img_tags:
            link = {k.lower(): v for k, v in link.items()}

            if "srcset" in link.keys():
                src_set_links = split_srcset(link["srcset"])
                for srcset_value in src_set_links:
                    links.append(prepare_link(srcset_value))

            if 'src' in link.keys():
                if "data:image" in link['src']:
                    if "data-srcset" in link.keys():
                        src_set_links = split_srcset(link["data-srcset"])
                        for srcset_value in src_set_links:
                            links.append(prepare_link(srcset_value))

                    if "data-src" in link.keys():
                        links.append(prepare_link(link["data-src"]))

                links.append(prepare_link(link["src"]))

        # remove duplicates
        [self.image_links.append(item) for item in links if item not in self.image_links]
        return

    @staticmethod
    def _downloader_task(url_: str, path: str):
        """
        Worker to handle image links: it download normal links or convert encoded images to files
        :param url_: link to download
        :param path: folder to save
        :return:
        """
        if url_.startswith('data:image'):
            # not need to download, just convert value to picture and save it
            url_ = url_.replace("data:image/", "").replace(';', ',', 1)
            parts = url_.split(',')
            encoded_string = parts[-1]
            encoder_type = parts[-2]
            file_format = parts[-3]
            if encoder_type == "base64":
                image_data = base64.b64decode(encoded_string)
            else:
                assert False, f"This encoder {encoder_type} type doesn't support"
            filename = Path(str(zlib.crc32(image_data)) + "." + str(file_format))
            with open(Path(path / filename), 'wb+') as file:
                file.write(image_data)
        else:
            response = fetch_url(url_)
            if "?" in url_:
                url_ = url_.split("?")[0]
            extension = Path(url_).suffix
            if not extension:
                extension = ".png"
            filename = Path(sanitize_name(Path(url_).stem)[:ScrapImg.MAX_FILENAME_LEN] + extension)
            if Path(path / filename).exists():
                filename = Path(sanitize_name(Path(url_).stem)[:ScrapImg.MAX_FILENAME_LEN] + "_" +
                                str(zlib.crc32(url_.encode())) + extension)
            with open(Path(path / filename), 'wb+') as out_file:
                out_file.write(response.content)

    def get_images_links(self):
        """
        Get webpage, parse it and make a lists for <img../> and for <link .. as="style"/>
        :return: amount of <img> tags, amount of found css files
        """
        response = fetch_url(self.url)
        parser = ImgTagAndCssParser(self.url)
        parser.feed(response.text)

        self._prepare_image_links(parser.img_tags)
        self._prepare_css_links(parser.css_links)

        return len(parser.img_tags), len(parser.css_links)

    def download_images(self):
        threads = []
        for link in self.image_links:
            threads.append(Thread(target=ScrapImg._downloader_task, args=(link, self.path)))
        for thread in threads:
            thread.start()
            time.sleep(0.01)
        for thread in threads:
            thread.join()
        return len(threads)

    def __str__(self):
        files = [f for f in Path("." / self.path).iterdir() if f.is_file()]
        string = "List of images from webpage:\n"
        for link in self.image_links:
            if "data:image" in link:
                string += f"\t {link[:128]}... \n"
            else:
                string += f"\t {link} \n"
        string += f"List of files in {self.path} folder:\n"
        for f in files:
            string += f"\t {f} size={f.stat().st_size} \n"
        string += f"Amount of links={len(self.image_links)}, files={len(files)}"
        return string

    def scrap_images(self, verbose=False):
        self._prepare_folder()
        self.get_images_links()
        self.download_images()
        if verbose:
            print(self)


if __name__ == '__main__':
    print("Example of using scrapimg: ")
    url = "yle.fi/a/74-20112293"
    print(f"Try to download all images from {url}")

    s = ScrapImg(url, "niceFolder")
    s.scrap_images(True)
