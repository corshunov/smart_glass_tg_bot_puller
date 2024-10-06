import asyncio
from datetime import datetime
from os import getenv
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command

frame_fext = "jpg"
video_fext = "mp4"

cwd = Path.cwd()
data_dpath = cwd / "data"
ref_frames_dpath = data_dpath / "ref_frames"
videos_dpath = data_dpath / "videos"

controller_dpath = Path.home() / "smart_glass" / "controller"
controller_data_dpath = controller_dpath / "data"
controller_ref_frames_dpath = controller_data_dpath / "ref_frames"
controller_videos_dpath = controller_data_dpath / "videos"

controller_recording_video_fname = f"recording.{video_fext}"

CHAT_ID = getenv("CHAT_ID")
TOKEN = getenv("PULLER_BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)

def prepare_folders():
    data_dpath.mkdir(exist_ok=True)
    ref_frames_dpath.mkdir(exist_ok=True)
    videos_dpath.mkdir(exist_ok=True)

async def send_message():
    await asyncio.sleep(5)

    while True:
        existing_frames = sorted([i for i in controller_ref_frames_dpath.iterdir() if i.suffix == f".{frame_fext}"])
        if len(existing_frames) > 0:
            fpath = existing_frames[0]
            new_fpath = ref_frames_dpath / fpath.name
            fpath.rename(new_fpath)

            photo = FSInputFile(new_fpath)

            dt_str = fpath.with_suffix('').name.split('__')[-1]
            dt = datetime.strptime(dt_str, "%Y%m%d_%H%M%S")
            dt_str = dt.strftime("%d.%m.%Y at %H:%M:%S")
            caption_text = f"Reference frame\n({dt_str})"
            await bot.send_photo(CHAT_ID, photo, caption=caption_text)

        await asyncio.sleep(2)

        existing_videos = sorted([i for i in controller_videos_dpath.iterdir() if i.suffix == f".{video_fext}" and i.name != controller_recording_video_fname])
        if len(existing_videos) > 0:
            fpath = existing_videos[0]
            new_fpath = videos_dpath / fpath.name
            fpath.rename(new_fpath)

            video = FSInputFile(new_fpath)

            dt_str = fpath.with_suffix('').name.split('__')[-1]
            dt = datetime.strptime(dt_str, "%Y%m%d_%H%M%S")
            dt_str = dt.strftime("%d.%m.%Y at %H:%M:%S")
            caption_text = f"Video\n({dt_str})"
            await bot.send_video(CHAT_ID, video, caption=caption_text)

        await asyncio.sleep(2)

async def main():
    await bot.send_message(CHAT_ID, f"Smart Glass Puller started.")
    asyncio.create_task(send_message())
    await dp.start_polling(bot)
    

if __name__ == '__main__':
    prepare_folders()
    asyncio.run(main())
