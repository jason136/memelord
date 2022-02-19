import praw, os, requests
import unicodedata, re
import threading, queue
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
        print(f'downloading {url} in {images_path}')
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

images_path = './images/'
image_exts = ['.png', '.jpg', '.jpeg']
images = {}

def main():
    posts = subreddit.top('all', limit=None)
    if not os.path.exists(images_path):
        os.makedirs(images_path)

    for i in range(number_of_threads):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()

    for post in posts:
        title = post.title
        url = post.url
        _, ext = os.path.splitext(url)
        filepath = images_path + legalize(title) + ext
        if ext in image_exts:
            q.put([url, filepath])
    q.join()

main()