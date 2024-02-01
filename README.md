# FlickrCrawler

---


## How to use:

First you need the crawl the Flickr and get url of the images for your search text. Then you can download the images and
filter them using a user interface (e.g. to remove the outliers).

***
### Fetching urls for a search text:

Run fetch_urls.py to fetch image urls for a given tag. You can specify number of images you want, the date interval to
perform search on, the color code of the images you want, the license of the images, and some other options. For seeing
complete options you can check the code. Note that Flickr does not allow fetching more than 4000 thousand urls in a
single search. So, if you need to get more than 4000 images you should break your search into smaller time intervals by
specifying the start_date and days_interval parameters.

Example:

``python3 fetch_urls.py cats``

Tags: 
https://www.flickr.com/services/api/flickr.photos.search.html

---

### Downloading the images:

After you've fetched the urls, A meta.json file is created that contains the information of the found images. Now you
can call fetch_images.py to download the images according to the meta file. The images will be center cropped and
resized to the width and height provided as parameters. You can specify number of workers in parallel to speed up the
process.

Example:

``python3 fetch_images.py cats --num-workers=4``

---


### User interface for filtering the images

Once you have the meta file and have downloaded the images, you can prone the downloaded images and select the images
that you want to keep by calling select_images.py This will show you the images in a window and user can navigate and
add or delete images. You can use left and right arrow keys to navigate through images. For adding an image press the '
a' key and for deleting an image press the 'd' key. By pressing Esc key your choices will be saved, and you can continue
filtering the images at later time.

Example:

``python3 select_images.py cats``

When you're done with filtering the images, you can call extract_selected.py. This will copy the selected images to a
new folder and create a new meta file for the selected images.

---


## Flickrapi

The flickrapi library is not maintained and causes some errors. 
Specifically the `.getchildren()`  method creates errors.
You can simply replace the following line in `flickrapi/core.py`

```python
photoset = rsp.getchildren()[0]
```
with 

```python
photoset = list(rsp)[0]
```



