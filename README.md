# Report
## Task 1
### Solution

The solution for this task will be a console utility with one mandatory command-line argument: the URL, and a couple of optional ones: output folder and verbose mode. The algorithm is straightforward: process the arguments, validate the URL, prepare the output folder (cleaning it if necessary), parse the webpage, and download the images. The webpage is parsed using HTMLParser, which identifies <img .../> tags and CSS files. For CSS files, it extracts all URLs from url() functions if the file extensions are in [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".tif"]. For <img .../> tags, it retrieves all files from srcset or data-srcset, as well as from src or data-src. The list of files is then cleaned to remove duplicates, and each file is downloaded in a separate thread. If a file is in the <data:image...> format, it is decoded and saved, but only base64 encoding is supported.

Running the downloads in parallel is necessary because this part is the most time-consuming. Using threads instead of processes should suffice, as real parallelism is not required for this task—it's more about not waiting for the first image to finish downloading before starting the others. While it’s technically possible to parallelize the parsing and folder preparation, doing so would only be beneficial in rare cases, so it won't be implemented.

#### Tests

There are a couple of default libraries available to solve this task, such as BeautifulSoup, so it would be useful to compare the parsing results with them. This is implemented in the unit tests: several different webpages are processed both ways, and the expected images should match. The tests also check that the number of found image files equals the number of downloaded or created files.

#### Getting started

There is a jenkinsfile for parametrized pipeline, it will make unittest and download images from provided parameter and store them as artifacts.

```console
cd task1
pip3 install -r requirements.txt
python3 scrapimg/test_scrapimg.py
python3 main.py -u www.yle.fi/a/74-20112293 -p artifacts -v
```

## Task 2

### Solution

There is a demo application based on a static library with a CMake configuration. It is designed to work on Windows with Visual Studio 2019 and on Linux using GCC-9 within a Docker container. The Docker image uses a multistage build process.

#### Getting started
Windows:
```console
cd task2
cmake -B ./build -S . && cmake --build ./build
.\build\MathClient\Debug\MathClient.exe
```

Linux:
```console
cd task2
docker build -t mathclient:1 .
docker run mathclient:1
```