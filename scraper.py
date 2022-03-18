import praw, os, requests, datetime
import unicodedata, re
import threading, queue
import pandas as pd
import tokens, globals

number_of_threads = 30
q = queue.Queue()

def legalize(text, allow_unicode=False):
    text = str(text)
    if allow_unicode:
        text = unicodedata.normalize('NFKC', text)
    else:
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '-', text).strip('-_')

def download(url, filename):
    try:
        print(f'downloading {url} to {filename}')
        r = requests.get(url, allow_redirects=True)
        with open(filename, 'wb') as file:
            file.write(r.content)
    except Exception as e:
        print(f'error while downloading {url}: {e}')
        q.put([url, filename])
        q.join()

def worker():
    while True:
        meme = q.get()
        download(meme[0], meme[1])
        q.task_done()


def main():
    image_exts = ['.png', '.jpg', '.jpeg']
    dicts = {}
    keys = globals.keys
    memes_root = globals.memes_root
    
    reddit = praw.Reddit(client_id=tokens.REDDIT_ID, client_secret=tokens.REDDIT_SECRET, user_agent=tokens.REDDIT_AGENT)
    subreddit = reddit.subreddit('memes')
    posts = subreddit.top('day', limit=None)

    for i in range(number_of_threads):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
        
    download_count = 0
    for post in posts:
        url = post.url
        _, ext = os.path.splitext(url)
        if ext in image_exts:
            date_created = datetime.datetime.fromtimestamp(post.created).strftime("%m-%d-%y")
            if (date_created not in dicts):
                if (os.path.exists(f'{memes_root}/{date_created}/{date_created}.csv')):
                    dicts[date_created] = pd.read_csv(f'{memes_root}/{date_created}/{date_created}.csv', usecols=keys).to_dict(orient='list')
                else:
                    dicts[date_created] = dict.fromkeys(keys)
                    for key in keys:
                        dicts[date_created][key] = []
                    if not os.path.exists(f'{memes_root}/{date_created}'):
                        os.makedirs(f'{memes_root}/{date_created}')
            data = dicts[date_created]

            if (url in data['urls']):
                continue 

            data['urls'].append(url)
            data['scores'].append(post.score)
            data['timestamps'].append(datetime.datetime.fromtimestamp(post.created))

            legal_filename = f'{len(data["titles"])}_{legalize(post.title)}'
            filename = f'{memes_root}/{date_created}/{legal_filename}{ext}'

            data['titles'].append(post.title)
            data['filenames'].append(filename)
            data['extracted text'].append('')
            download_count += 1
            q.put([url, filename])
    q.join()
    
    for date, data in dicts.items():
        dataframe = pd.DataFrame.from_dict(data)
        csv = dataframe.to_csv(f'{memes_root}/{date}/{date}.csv', index=True, header=True)

    input(f"{download_count} files downloaded and {len(dicts.keys())} csv's written")

if __name__ == '__main__':
    main()