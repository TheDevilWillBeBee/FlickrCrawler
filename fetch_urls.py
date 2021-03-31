import os
import json
import argparse
import datetime
from tqdm import tqdm
from flickrapi import FlickrAPI


def build_parser():
    parser = argparse.ArgumentParser(description="""Fetch images from Flickr API for a given tag.""")
    parser.add_argument('tag', type=str)
    parser.add_argument('--out', type=str, default='data/')
    parser.add_argument('--key', type=str)
    parser.add_argument('--secret', type=str)
    parser.add_argument('--start-date', type=str)
    parser.add_argument('--sorting', type=str, default='relevance', choices=['relevance', 'interestingness-desc'])
    parser.add_argument('--total', type=int, default=1)
    parser.add_argument('--days-interval', type=int, default=1)
    parser.add_argument('--per-page', type=int, default=50)
    parser.add_argument('--color-codes', type=str, default="-1")
    parser.add_argument('--license', type=int, default=2)  # 2 is Creative Common license
    return parser


def fetch_urls(args):
    year, month, day = map(int, args.start_date.split('-'))
    start_date = datetime.date(year, month, day)
    meta = {}
    seen_uids = {}
    last_id = 0
    if not os.path.exists(os.path.join(args.out, args.tag)):
        os.makedirs(os.path.join(args.out, args.tag))
    else:
        with open(os.path.join(args.out, f"{args.tag}/meta.json"), 'r') as f:
            meta = json.load(f)
            for k in meta:
                uid = meta[k]['metadata']['uid']
                seen_uids[uid] = 1
                last_id = max(int(k), last_id)

    n = 0
    per_page = 500
    total = 0
    duplicate = 0
    delta_n_per_page = -1
    flickr = FlickrAPI(args.key, args.secret)
    end_date = start_date + datetime.timedelta(days=args.days_interval)
    kwargs = {
        'text': args.tag,
        'tag_mode': 'any',
        'min_upload_date': str(start_date),
        'max_upload_date': str(end_date),
        'extras': 'url_o,color_codes,owner_name,license,owner,id,tags,date_upload',
        'per_page': 500,
        'license': args.license,  # Commercial use allowed
        'sort': args.sorting,
        #         'sort':'interestingness-desc'
    }
    if args.color_codes != '-1':
        kwargs['color_codes'] = args.color_codes
    photos = flickr.walk(**kwargs)

    t = tqdm(photos, desc=f'Fetching Images {n}/{args.total} from {start_date} to {end_date}')
    for photo in t:
        if total % per_page == 0:
            # No new image found in the last page
            if delta_n_per_page == 0:
                break
            delta_n_per_page = 0
        total += 1
        try:
            url = photo.get('url_o')
            if url is not None:
                author_id = photo.get('owner')
                photo_id = photo.get('id')
                photo_uid = f'{author_id}/{photo_id}'
                if photo_uid in seen_uids:
                    duplicate += 1
                    continue

                author = photo.get('ownername')
                photo_title = photo.get('title')
                photo_url = f"https://flickr.com/{author_id}/{photo_id}"
                color_code = photo.get('color_codes')
                tags = photo.get('tags')
                license = photo.get('license')
                upload_date = datetime.datetime.fromtimestamp(int(photo.get('dateupload')))
                print(upload_date)
                n += 1
                meta[str(n + last_id).zfill(6)] = {
                    "metadata": {
                        "photo_url": photo_url,
                        "download_url": url,
                        "photo_title": photo_title,
                        "author": author,
                        "license": license,
                        "author_id": author_id,
                        "photo_id": photo_id,
                        "uid": photo_uid,
                        "tags": tags,
                        "color_code": color_code,
                        "upload_date": str(upload_date),
                        "rank": str(n / total),
                    }
                }
                delta_n_per_page += 1
                seen_uids[photo_uid] = 1

        except:
            pass

        if n >= args.total:
            break
        t.set_description(
            f"Fetching Images {n}/{args.total}, Duplicate: {duplicate}/{total} {start_date} to {end_date}",
            refresh=True)

    with open(os.path.join(args.out, f"{args.tag}/meta.json"), 'w') as f:
        f.write(json.dumps(meta, indent=4, sort_keys=True))


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    fetch_urls(args)
