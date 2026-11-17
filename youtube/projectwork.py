import requests
import json
from datetime import date

import os
from dotenv import load_dotenv
load_dotenv(dotenv_path='./.env')

API_KEY =os.getenv('API_KEY')
CHANNEL = 'Mrbeast'
max_results=50

def get_playlist_id():
    try:
        playlist_url=F'https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL}&key={API_KEY}'
        response = requests.get(playlist_url)
        response.raise_for_status()
        data = response.json()
       # print(json.dumps(data,indent=4))

        playlist_id=(data['items'][0]['contentDetails']['relatedPlaylists']['uploads'])
        #print(playlist_id)
        return playlist_id
    except requests.exceptions.RequestException as e:
     raise e
    
def get_video_id(playlist_id):
   video_id=[]
   page_token=None
   try:
       video_id_url = F'https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={max_results}&playlistId={playlist_id}&key={API_KEY}'
       while True:
       
          url=video_id_url 
        
          if page_token:
           url += f'&pageToken={page_token}'
          response = requests.get(url)
          response.raise_for_status()
          data = response.json()

          for item in data.get('items', []):
           video_id.append(item['contentDetails']['videoId'])
          page_token = data.get('nextPageToken')
 
          if not page_token:
                 break

       return video_id
   except requests.exceptions.RequestException as e:
        raise e
if __name__ == '__main__':
    playlist_id = get_playlist_id()
    video_id = get_video_id(playlist_id)
    print((video_id))

def get_video_data(video_id):
    extracted_data = []

    try:
        for start in range(0, len(video_id), 50):
            batch = video_id[start:start + 50]
            ids_string = ','.join(batch)

            video_data_url= f'https://youtube.googleapis.com/youtube/v3/videos?part=snippet,contentDetails,statistics&id={ids_string}&key={API_KEY}'
            response=requests.get(video_data_url)
            response.raise_for_status()
            data = response.json()
            for item in data.get('items',[]):
                extracted_data.append({
                    'video_id': item['id'],
                    'title': item['snippet']['title'],
                    'published_at': item['snippet']['publishedAt'],
                    'duration': item['contentDetails']['duration'],
                    'views': item['statistics'].get('viewCount'),
                    'likes': item['statistics'].get('likeCount'),
                    'comments': item['statistics'].get('commentCount'),
    })
        return extracted_data
    except requests.exceptions.RequestException as e:
       raise e
def save_to_json(data):
    filename = f'video_data_{date.today()}.json'

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return filename
if __name__=='__main__':
   playlist_id = get_playlist_id()
   video_id = get_video_id(playlist_id)
   video_data= get_video_data(video_id)
   print(len(video_data))
   print(video_data[0])
   saved_file = save_to_json(video_data)

   print(len(video_id), len(video_data))
   print('Saved to', saved_file)
   