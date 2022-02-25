import praw, os, requests, datetime
import unicodedata, re
import threading, queue
import pandas as pd
import tokens

def legalize(text, allow_unicode=False):
    text = str(text)
    if allow_unicode:
        text = unicodedata.normalize('NFKC', text)
    else:
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '-', text).strip('-_')

def download(url, filepath):
    try:
        print(f'downloading {url} to {filepath}')
        r = requests.get(url, allow_redirects=True)
        with open(filepath, 'wb') as file:
            file.write(r.content)
        return True
    except Exception as e:
        print(f'error while downloading {url}: {e}')
        if download(url, filepath):
            return True

q = queue.Queue()
number_of_threads = 30

def worker():
    while True:
        meme = q.get()
        download(meme[0], meme[1])
        q.task_done()

memes_root = './memes'
image_exts = ['.png', '.jpg', '.jpeg']

keys = ['ids', 'titles', 'filenames', 'urls', 'scores', 'timestamps']
dicts = {}

def main():
    
    reddit = praw.Reddit(client_id=tokens.REDDIT_ID, client_secret=tokens.REDDIT_SECRET, user_agent=tokens.REDDIT_AGENT)
    subreddit = reddit.subreddit('memes')
    posts = subreddit.top('day', limit=None)

    # if not os.path.exists(memes_root):
    #     os.makedirs(memes_root)

    for i in range(number_of_threads):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()

    for post in posts:
        url = post.url
        _, ext = os.path.splitext(url)
        if ext in image_exts:
            date_created = datetime.datetime.fromtimestamp(post.created).strftime("%m-%d-%y")
            if (date_created not in dicts):
                if (os.path.exists(f'{memes_root}/{date_created}/{date_created}.csv')):
                    dicts[date_created] = pd.read_csv(f'{memes_root}/{date_created}/{date_created}.csv').to_dict()
                else:
                    dicts[date_created] = dict.fromkeys(keys)
                    for key in keys:
                        dicts[date_created][key] = []
                    if not os.path.exists(f'{memes_root}/{date_created}'):
                        os.makedirs(f'{memes_root}/{date_created}')
            data = dicts[date_created]

            id = url[18:31]
            if (id in data['ids']):
                continue 

            data['ids'].append(id)
            data['urls'].append(url)
            data['scores'].append(post.score)
            data['timestamps'].append(datetime.datetime.fromtimestamp(post.created))

            legal_title = legalize(post.title)
            if (post.title in data['titles']):
                legal_title += f' ({id})'
            filename = f'{memes_root}/{date_created}/{legal_title}{ext}'

            data['titles'].append(post.title)
            data['filenames'].append(filename)
            q.put([url, filename])
    q.join()

    for date, data in dicts.items():
        dataframe = pd.DataFrame.from_dict(data)
        csv = dataframe.to_csv(f'{memes_root}/{date}/{date}.csv', index=True, header=True)

main()