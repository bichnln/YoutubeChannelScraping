import json
import pprint
import requests
import connection
from youtube_stats import YoutubeAPI
from models import Video, Stats 
from datetime import date, datetime
from pymongo import MongoClient
from tqdm import tqdm


with open('youtube_credentials.json') as json_file:
    data = json.load(json_file)
    API_KEY = data['API_KEY']

yt = YoutubeAPI(API_KEY)

# create a client connecting to localhost on port 27017
client = MongoClient('localhost', 27017)
db = client['dreamcatcher']

videoCollection = db['videos']           # store information of videos
statisticsCollection = db['statistics']  # store statistics data of videos (view count..)
statsCollection = db['stats'] # store daily stats with name instead of vid
testing = db['test']

# v is video typed
# add a video to videoCollection
def add_videos(v):
    # check if this video has already been added yet before adding
    if (videoCollection.count_documents({"vid": v.vid}) == 0):
        video = {"vid": v.vid,
                 "title": v.title,
                 "playlist": v.playlist,
                 "published_date": v.publishedDate}
        videoCollection.insert_one(video)
        #testing.insert_one(video)
        print("\nVideo {title} added to database!".format(title=v.title))
    else:
        print("\nRecord {vid} already exists!".format(vid = v.vid))

# s is Stats typed
def add_stats(s):
    if (statisticsCollection.count_documents({"vid": s.vid, "recorded_date": s.recordedDate}) == 0):
        stat = {"vid": s.vid,
                "recorded_date": s.recordedDate,
                "viewCount": s.viewCount, 
                "likeCount": s.likeCount,
                "dislikeCount": s.dislikeCount,
                "commentCount": s.commentCount}
        # statisticsCollection.insert_one(stat)
        statsCollection.insert_one(stat)
        print("\nVideo {vid} added to database!".format(vid=s.vid))
    else:
        print("\nRecord {vid} already counted for today {today}!".format(vid=s.vid, today=str(s.recordedDate)))


# add all videos' profiles from playlist to database
def add_video_from_playlist(playlist_id):
    playlist_title = yt.get_playlist_title(playlist_id)
    playlist_items = yt.get_playlist_items(playlist_id)
    print(playlist_title)
    for item in tqdm(playlist_items):
        video = Video(item['contentDetails']['videoId'],
                      item['snippet']['title'],
                      playlist_title,
                      item['contentDetails']['videoPublishedAt'])
        add_videos(video)

def setup_video_profiles_from_playlist_file(playlist_ids_file):
    with open(playlist_ids_file) as file_of_ids:
        data = json.load(file_of_ids)
        # loop through items in data['playlists']
        for playlist in tqdm(data['playlists']):
            add_video_from_playlist(playlist['id'])

def get_today_stats():
    now = datetime.utcnow()
    # get all video in database
    videos = tqdm(videoCollection.find({}))
    for v in videos:
        data = yt.get_video_stats(v['vid'])
        stats = Stats(v['vid'], now,
                      data['viewCount'], data['likeCount'], data['dislikeCount'], data['commentCount'])
        add_stats(stats)




if __name__ == "__main__":
    setup_video_profiles_from_playlist_file("dreamcatcher_ids.json")
    get_today_stats()
    
    

    




    

        
