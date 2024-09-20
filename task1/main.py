#!/usr/bin/python

import argparse
import sys
from scrapimg.scrapimg import ScrapImg

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description="Simple script to download all images from provided url")
    arg_parser.add_argument("-u", "--url", type=str, help="url to page for getting images from", required=True)
    arg_parser.add_argument("-p", "--path", type=str, help="path to download images", default="./images")
    arg_parser.add_argument("-v", "--verbose", action="store_true", help="print additional info")
    args = arg_parser.parse_args()

    scrap_img = ScrapImg(url_=args.url, folder_path=args.path)
    try:
        scrap_img.scrap_images(args.verbose)
    except Exception as e:
        if args.verbose:
            print(f"e")
        sys.exit(1)

    sys.exit(0)





