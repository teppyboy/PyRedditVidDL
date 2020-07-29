# PyRedditVidDL - a simple script for downloading Reddit videos.
## Installing
- Windows + Linux:
1. Download the executable file in releases.
2. Run the file
- macOS (and any other OS that supports Python):
1. Clone this repo
2. Execute this command:
```bash
pip install -r requirements.txt
```
3. Use `python3 main.py` to launch.
### How-to Use
- This script supports start with arguments (arguments are Reddit post(s) ID/URL). By default if start without argument it'll ask you reddit post(s) URL/ID to download video(s).
### Building
1. Clone the project
- Using Git
```bash
git clone https://github.com/teppyboy/PyRedditVidDL
cd PyRedditVidDL
```
- Using wget (Linux)
```bash
wget https://github.com/teppyboy/PyRedditVidDL/archive/master.zip -O PyRedditVidDL.zip
unzip PyRedditVidDL.zip
cd PyRedditVidDL
```
2. Creating VENV (Optional, recommended)
- Windows (in cmd)
```bash
py -m venv venv
venv/Scripts/activate.bat
```
- Linux
```bash
python3 -m venv venv
venv/bin/activate
```
3. Installing deps and compile
```
pip install -r requirements.txt
pyinstaller --onefile main.py
```
- This should create a file called main (with extensions) that is corresponding to your OS, and pyinstaller can only build file for the OS that executing it.