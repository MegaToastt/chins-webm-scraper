import requests
from requests.exceptions import HTTPError
import functools
import html
import os
import glob
from pprint import pprint

API_BASE = "https://a.4cdn.org"
BOARDS_URL = f'{API_BASE}/boards.json'

def catalog_url(board):
  return f"{API_BASE}/{board}/catalog.json"

def webm_url(board, tim):
  return f"https://i.4cdn.org/{board}/{tim}.webm"


def thread_url(board, op_num):
  return f"{API_BASE}/{board}/thread/{op_num}.json"

def get_post_title(thread):
  if 'sub' in thread:
    return thread['sub']
  elif 'com' in thread:
    return thread['com']
  else:
    return 'TITLE NOT FOUND'

def get_board_from_input():
  res = requests.get(BOARDS_URL)
  boards = res.json()['boards']

  while True:
    print("=============================")
    try:
      board_input = input('Pick a board: ')
    except ValueError:
      print("---")
      print("ERR: Enter proper shit.")
      continue
    if board_input not in [board['board'] for board in boards]:
      print("---")
      print("ERR: Pick an actual board.")
      continue
    else:
      break
  return board_input

def get_search_term_from_input():
  while True:
    print("=============================")
    try:
      term_input = input('Enter search term: ')
    except ValueError:
      print("---")
      print("ERR: Enter proper shit.")
      continue
    else:
      break
  return term_input


def get_threads(board, term):
  try:
    res = requests.get(catalog_url(board))
    res.raise_for_status()
  except HTTPError as err:
    print(f'HTTP ERROR: {err}')
  except Exception as err:
    print(f'OTHER ERROR: {err}')
  else:
    # filter for ygyl threads
    content = res.json()
    threads = functools.reduce(lambda a, b: a + b['threads'], content, [])
    threads = list(filter(lambda a: term in get_post_title(a).lower(), threads))
    return threads

def get_thread_from_input(board):
  term = get_search_term_from_input()
  threads = get_threads(board, term)
  if threads is None or len(threads) == 0:
    raise Exception('No results returned from search term')
  thread_idx = 0
  # have user choose which thread
  while True:
    print("=============================")
    try:
      for i, thread in enumerate(threads):
        print(f'{i}: {get_post_title(thread)}')
      thread_idx = int(input('Pick a thread: '))
    except ValueError:
      print("---")
      print("ERR: Pick a number retard.")
      continue
    if thread_idx < 0 or thread_idx >= len(threads):
      print("---")
      print("ERR: Pick a listed number idiot.")
      continue
    else:
      break
  return threads[thread_idx]

def get_webms_from_posts(board, posts):
  res = []
  for post in posts:
    if 'filename' not in post: continue
    if 'ext' not in post: continue
    if post['ext'] != ".webm": continue
    res.append((webm_url(board, post['tim']), post['filename']))
  return res

def download_and_save_webms(webms):
  # create downloads dir if doesnt exist
  DOWNLOAD_DIR = 'webms'
  CONVERT_DIR = 'mp3'
  if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)
  if not os.path.exists(CONVERT_DIR):
    os.makedirs(CONVERT_DIR)

  # clear the file directories
  files_to_delete = glob.glob(f'{DOWNLOAD_DIR}/*.webm')
  for f in files_to_delete: os.remove(f)
  files_to_delete = glob.glob(f'{CONVERT_DIR}/*.mp3')
  for f in files_to_delete: os.remove(f)

  # download all the webms
  for webm in webms:
    print(f'Downloading {webm}.webm...')
    res = requests.get(webm[0])
    open(f'{DOWNLOAD_DIR}/{webm[1]}.webm', 'wb').write(res.content)
  
  # convert to mp3
  # for filename in os.listdir(DOWNLOAD_DIR):
  #   print(f'Converting {filename} to mp3...')
  #   os.system(f'ffmpeg -i {DOWNLOAD_DIR}/{filename} {CONVERT_DIR}/{filename.split(".")[0]}.mp3')

def run():
  board = get_board_from_input()
  thread_details = get_thread_from_input(board)
  thread_content_res = requests.get(thread_url(board, thread_details['no']))
  thread_content = thread_content_res.json()
  posts = thread_content['posts']

  webms = get_webms_from_posts(board, posts)
  download_and_save_webms(webms)

run()