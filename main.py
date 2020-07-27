print("Initalizing...")
import praw, prawcore, requests, json, subprocess, os, sys, shutil, zipfile, glob
from pathlib import Path
reddit = None
currentDir = os.getcwd()
praw_ini_file = Path(f'{currentDir}/praw.ini')
if not praw_ini_file.is_file():
    with open("praw.ini", "w") as praw_ini_write: #Weird flex but ok it works
        praw_ini_write.write("""[DEFAULT]
# A boolean to indicate whether or not to check for package updates.
check_for_updates=True

# Object to kind mappings
comment_kind=t1
message_kind=t4
redditor_kind=t2
submission_kind=t3
subreddit_kind=t5
trophy_kind=t6

# The URL prefix for OAuth-related requests.
oauth_url=https://oauth.reddit.com

# The amount of seconds to ratelimit
ratelimit_seconds=5

# The URL prefix for regular requests.
reddit_url=https://www.reddit.com

# The URL prefix for short URLs.
short_url=https://redd.it

# The timeout for requests to Reddit in number of seconds
timeout=16
""")
    print("Created praw.ini.")
config_file = Path(f'{currentDir}/config.json')
if config_file.is_file():
    try:
        with open(f'{currentDir}/config.json') as f:
            data = json.load(f)
            reddit = praw.Reddit(client_id=data["reddit"]["client_id"],client_secret=data["reddit"]["client_secret"],password=data["reddit"]["password"],user_agent="PyRedditVidDL",username=data["reddit"]["username"])
            # Vaild account check.
            try:
                subreddit = reddit.subreddit("all") 
                subreddit.random()
            except prawcore.exceptions.ResponseException:
                print("Error! Not a vaild reddit account, please config the account in config.json")
                reddit = None
    except OSError as ex:
        print(f"An error occured\n{ex}")
        reddit = None
else:
    config = {}
    config["reddit"] = {}
    config["reddit"]["client_id"] = ""
    config["reddit"]["client_secret"] = ""
    config["reddit"]["username"] = ""
    config["reddit"]["password"] = ""
    config_data = json.dumps(config, indent=4, sort_keys=True)
    with open("config.json", "w") as config_json_file:
        config_json_file.write(config_data)
    print("config.json dosen't exists! I've created a demo file for you.")
ffmpeg_exe = Path(f'{currentDir}/ffmpeg/ffmpeg.exe')
if not ffmpeg_exe.is_file():
    print("FFMpeg not found, downloading...")
    try:
        with requests.get("https://ffmpeg.zeranoe.com/builds/win64/shared/ffmpeg-4.3-win64-shared.zip", stream=True) as r:
            with open(f"{currentDir}/ffmpeg.zip", 'wb') as f:
                shutil.copyfileobj(r.raw, f)
            print("Extracting FFMpeg...")
            Path(currentDir + "/ffmpeg_tmp").mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(f"{currentDir}/ffmpeg.zip", 'r') as zip_ref:
                zip_ref.extractall(f"{currentDir}/ffmpeg_tmp")
            for root, dirs, files in os.walk(f"{currentDir}/ffmpeg_tmp"):
                if "ffmpeg.exe" in files:
                    bin_path = os.path.dirname(os.path.join(root, "ffmpeg.exe"))
                    Path(currentDir + "/ffmpeg").mkdir(parents=True, exist_ok=True)
                    for filename in glob.glob(os.path.join(bin_path, '*.*')):
                        shutil.copy(filename, f"{currentDir}/ffmpeg")
                    print("Removing temporary files...")
                    os.remove("ffmpeg.zip")
                    shutil.rmtree("ffmpeg_tmp")
                    print("Done!")
                    break
    except (requests.exceptions.RequestException, OSError) as ex:
        print(f"An error occured, cleaning downloaded files...\n{ex}")
        os.remove("ffmpeg.zip")
        shutil.rmtree("ffmpeg_tmp")
        shutil.rmtree("ffmpeg")
        reddit = None
if reddit != None:
    print("Sucessfully initalized!")
    post_ids = sys.argv[1:]
    if post_ids == None or post_ids == []:
        post_ids = input("Welcome to PyRedditVidDL, paste the submission URL/ID here (use spaces to fetch video from multiple submission): ").split(" ")
    else:
        print("PyRedditVidDL has detected arguments, fetching post from args...")
        post_ids = sys.argv[1:]
    totalVidName = []
    for post_id in post_ids:
        print(f'Fetching post [{post_id}]...')
        try:
            post = reddit.submission(url=post_id)
        except (praw.exceptions.InvalidURL, prawcore.exceptions.NotFound, prawcore.exceptions.BadRequest):
            print("[WARN] Input is not a vaild URL.")
            post = reddit.submission(id=post_id)
            try:
                boolean = post.over_18
            except (prawcore.exceptions.BadRequest, prawcore.exceptions.NotFound):
                print("[WARN] Input is not a vaild ID.")
                post = None
        if post != None:
            post_url_json = "https://www.reddit.com" + post.permalink + ".json"
            print(f"Post JSON URL = {post_url_json}")
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'} #emulating win10 x64 chrome 84
            resp = requests.get(post_url_json, headers=headers)
            post_json_array = json.loads(resp.text) #for some reason reddit json is json array.
            video_url = None
            for i in post_json_array:
                for ii in i["data"]["children"]:
                    try:
                        print("Video URL: " + ii["data"]["secure_media"]["reddit_video"]["hls_url"])
                        video_url = ii["data"]["secure_media"]["reddit_video"]["hls_url"]
                        break
                    except:
                        pass #why? bc why not.
            if video_url != None:
                patchedPostTitle = post.title.replace('\"', '')
                vidName = f"{patchedPostTitle} - {post.id}.mp4"
                totalVidName.append(vidName)
                print(f"Downloading to {vidName}...")
                Path(currentDir + "/Videos").mkdir(parents=True, exist_ok=True)
                ffmpeg = subprocess.call(f'{currentDir}/ffmpeg/ffmpeg.exe -y -i "{video_url}" -c copy -bsf:a aac_adtstoasc "{currentDir}/Videos/{vidName}"')
                if ffmpeg == 0:
                    print(f"Sucessfully download Video into {vidName} inside Videos directory!")
                else:
                    vido = Path(f'{currentDir}/Videos/{vidName}')
                    if vido.is_file():
                        print(f"FFMpeg returns 1 but the file is exists, maybe the video is downloaded into {vidName} inside Videos directory.")
                    else:
                        print("Failed to download video.")
            else:
                print("Post is not a video, nothing to download.")
        else:
            print("Failed to fetch post, is that an invalid post?")
    print(f'Total video downloaded: {", ".join(totalVidName)}')
print("Completed work.")
input("Press enter to exit program...\n")