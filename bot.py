import requests
import os
import json
from bs4 import BeautifulSoup

cookies = os.environ['cookies']
url = 'https://app.dataannotation.tech/workers/projects'
telegram = os.environ['TELEGRAM_TOKEN']
chat = os.environ['CHAT_ID']
path = 'IDS.txt'
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:147.0) Gecko/20100101 Firefox/147.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'pl,en-US;q=0.9,en;q=0.8',
    # 'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Referer': 'https://accounts.google.com/',
    'Alt-Used': 'app.dataannotation.tech',
    'Connection': 'keep-alive',
    # 'Cookie': 'conv_session=eyJpZCI6ImZiMTZmZWE4OTI5OTZkMDI1MTUxMjdlNTkwZDZhZWVkYTUwNThkZGVmZGVjM2RlODM3N2E1YTYxZWM2ODY3M2NmNjVhMGU3ODNhZDAxZDkyMDYxNTBjNDcxNiIsImxpbmtpbmdfcmVxdWlyZWQiOmZhbHNlfQ%3D%3D; gondor-main=a3a300b1ff8e92d7510cdfa953d40158; AMP_50c088a20a=JTdCJTIyZGV2aWNlSWQlMjIlM0ElMjIyMjE3MWZmNS04M2UwLTQwZjgtOGEzZS1iMmRkZjUyZWU1ZjQlMjIlMkMlMjJ1c2VySWQlMjIlM0ElMjI1YTI2NWY5YS1mYTg5LTQyOTktOTcwMy0yNWE3ZDAzZjdmNTYlMjIlMkMlMjJzZXNzaW9uSWQlMjIlM0ExNzcxOTA4ODg5ODc4JTJDJTIyb3B0T3V0JTIyJTNBZmFsc2UlMkMlMjJsYXN0RXZlbnRUaW1lJTIyJTNBMTc3MTkwOTk5ODg2MCUyQyUyMmxhc3RFdmVudElkJTIyJTNBMTklMkMlMjJwYWdlQ291bnRlciUyMiUzQTUlN0Q=; AMP_MKTG_50c088a20a=JTdCJTIycmVmZXJyZXIlMjIlM0ElMjJodHRwcyUzQSUyRiUyRmFjY291bnRzLmdvb2dsZS5jb20lMkYlMjIlMkMlMjJyZWZlcnJpbmdfZG9tYWluJTIyJTNBJTIyYWNjb3VudHMuZ29vZ2xlLmNvbSUyMiU3RA==',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-User': '?1',
    'DNT': '1',
    'Sec-GPC': '1',
    'Priority': 'u=0, i'
}

def get_response():
    response = requests.get(url, cookies=cookies, headers=headers)
    print(f'Response status code: {response.status_code}')
    
    return response

def parse_html(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    div = soup.find('div', {'id':'workers/WorkerProjectsTable-hybrid-root'})
    print(f'Data div found: {div is not None}')
    data_props = div['data-props']
    data = json.loads(data_props)
    projects = data['dashboardMerchTargeting']['projects']
    
    return projects

def get_ids(projects):
    ids = [i['id'] for i in projects]
    
    return ids

def save_ids(ids):
  sids = '\n'.join(ids)
  with open(path, 'w') as f:
    f.write(sids)
    print('IDs updated!')

  f.close()
  
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{telegram}/sendMessage"
    
    payload = {
        "chat_id": chat,
        "text": text
    }
    
    response = requests.post(url, data=payload)
    print("Telegram status:", response.status_code)

def check_updates(ids):
  try:
    with open(path, 'r') as f:
      old = set([id.strip() for id in f.readlines()])
      new = set(ids)
      n = len(new - old)

      if n > 0:
        send_telegram_message(f"You've got {n} new projects!")
        save_ids(ids)

      else:
        print('Nothing new :(')

      if len(new) < len(old):
        print('Less IDs than before.')
        save_ids(ids)

      f.close()
    
  except:
    print(f'Wrong path: {path}')
    send_telegram_message(f'Error with file {path}!')

def main():
    response = get_response()
    projects = parse_html(response)
    ids = get_ids(projects)
    try:
        if os.path.exists(path):
            check_updates(ids)
        elif not os.path.exists(path):
            save_ids(ids)
            check_updates(ids)
    except:
        print('Error on main!')
        
if __name__ == "__main__":
    main()
