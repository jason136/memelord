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

reddit = praw.Reddit(client_id=tokens.REDDIT_ID, client_secret=tokens.REDDIT_SECRET, user_agent=tokens.REDDIT_AGENT)
subreddit = reddit.subreddit('memes')

images_root = './images'
images_path = f'{images_root}/{datetime.date.today().strftime("%m-%d-%y")}'
image_exts = ['.png', '.jpg', '.jpeg']

def main():
    posts = subreddit.hot(limit=None)
    if not os.path.exists(images_path):
        os.makedirs(images_path)

    for i in range(number_of_threads):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()

    count = 0
    ids, titles, filenames, urls, scores, timestamps  = ([] for x in range(6))

    for post in posts:
        url = post.url
        _, ext = os.path.splitext(url)
        if ext in image_exts:
            ids.append(count)
            urls.append(url)
            scores.append(post.score)
            timestamps.append(datetime.datetime.fromtimestamp(post.created))

            legal_title = legalize(post.title)
            if (post.title in titles):
                legal_title += f'({count})'
            filename = f'{images_path}/{legal_title}{ext}'

            titles.append(post.title)
            filenames.append(filename)
            count += 1
            q.put([url, filename])
    q.join()

    dataframe = pd.DataFrame({
        'IDs': ids,
        'Filenames': filenames,
        'Titles': titles,
        'Urls': urls,
        'Scores': scores,
        'Timestamps': timestamps
    })
    csv = dataframe.to_csv(f'{images_path}/data.csv', header=True)

main()