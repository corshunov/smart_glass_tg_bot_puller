from os import getenv
from pathlib import Path

from aiogram import Bot, Dispatcher


cwd = Path.cwd()
data_dpath = cwd / "data"
ref_frames_dpath = data_dpath / "ref_frames"
videos_dpath = data_dpath / "videos"

controller_dpath = Path.home() / "smart_glass" / "controller"
controller_data_dpath = controller_dpath / "data"
controller_ref_frames_dpath = controller_data_dpath / "ref_frames"
controller_videos_dpath = controller_data_dpath / "videos"

CHAT_ID = getenv("CHAT_ID")
TOKEN = getenv("PULLER_BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)

def main():
    bot.send_message(CHAT_ID, f"Smart Glass Puller started.")
    
    #while True:

if __name__ == '__main__':
    main()
