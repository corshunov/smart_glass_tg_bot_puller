import asyncio
from datetime import datetime
from os import getenv
from pathlib import Path
import subprocess
import sys

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

frame_fext = "jpg"
video_fext = "mp4"

cwd = Path.cwd()
data_dpath = cwd / "data"
ref_frames_dpath = data_dpath / "ref_frames"
videos_dpath = data_dpath / "videos"

temperature_fpath = Path(r"/sys/class/thermal/thermal_zone0/temp")
temperature_log_fpath = data_dpath / "temp_log"

controller_dpath = Path.home() / "smart_glass" / "controller"
controller_data_dpath = controller_dpath / "data"
controller_ref_frames_dpath = controller_data_dpath / "ref_frames"
controller_videos_dpath = controller_data_dpath / "videos"

recording_video_fname = f"recording.{video_fext}"

manual_mode_fpath = controller_data_dpath / "manual_mode"
glass_state_on_fpath = controller_data_dpath / "glass_state_on"

if len(sys.argv) == 2 and sys.argv[1] == "--dev":
    CHAT_ID = getenv("CHAT_ID_DEV")
else:
    CHAT_ID = getenv("CHAT_ID")

TOKEN = getenv("PULLER_BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)

def prepare_folders():
    data_dpath.mkdir(exist_ok=True)
    ref_frames_dpath.mkdir(exist_ok=True)
    videos_dpath.mkdir(exist_ok=True)

def is_private_user(msg):
    if msg.chat.id == msg.from_user.id:
        return True

    return False

async def send_temperature():
    await asyncio.sleep(5)

    while True:
        await asyncio.sleep(300)

        with temperature_fpath.open('r') as f:
            text = f.read()
            t_cpu = int(text) / 1000

        text = subprocess.check_output(["vcgencmd", "measure_temp"])
        text = text.decode()
        t_gpu = float(text.split('=')[-1].split("'")[0])
            
        with temperature_log_fpath.open('a') as f:
            dt_str = datetime.now().strftime("%Y%m%dT%H%M%S")
            f.write(f"{dt_str},{t_cpu:.1f},{t_gpu:.1f}\n")

        await bot.send_message(CHAT_ID, f"Temperature: {t_cpu:.1f} (CPU), {t_gpu:.1f} (GPU)")

async def send_updated_reference_frames():
    await asyncio.sleep(5)

    while True:
        await asyncio.sleep(5)

        files = sorted([i for i in controller_ref_frames_dpath.iterdir() if i.suffix == f".{frame_fext}"])
        if len(files) > 0:
            fpath = files[0]
            new_fpath = ref_frames_dpath / fpath.name
            fpath.rename(new_fpath)

            file = FSInputFile(new_fpath)

            dt_str = fpath.with_suffix('').name.split('__')[-1]
            dt = datetime.strptime(dt_str, "%Y%m%d_%H%M%S")
            dt_str = dt.strftime("%d.%m.%Y at %H:%M:%S")
            caption_text = f"Reference frame\n({dt_str})"
            await bot.send_photo(CHAT_ID, file, caption=caption_text)

async def send_videos():
    await asyncio.sleep(5)

    while True:
        await asyncio.sleep(5)

        files = sorted([i for i in controller_videos_dpath.iterdir() if i.suffix == f".{video_fext}" and i.name != recording_video_fname])
        if len(files) > 0:
            fpath = files[0]
            new_fpath = videos_dpath / fpath.name
            fpath.rename(new_fpath)

            file = FSInputFile(new_fpath)

            dt_str = fpath.with_suffix('').name.split('__')[-1]
            dt = datetime.strptime(dt_str, "%Y%m%d_%H%M%S")
            dt_str = dt.strftime("%d.%m.%Y at %H:%M:%S")
            caption_text = f"Video\n({dt_str})"
            await bot.send_video(CHAT_ID, file, caption=caption_text)

async def send_mode():
    await asyncio.sleep(5)

    manual_mode_flag = manual_mode_fpath.is_file()

    while True:
        await asyncio.sleep(2)

        prev_manual_mode_flag = manual_mode_flag
        manual_mode_flag = manual_mode_fpath.is_file()

        if prev_manual_mode_flag != manual_mode_flag:
            if manual_mode_flag:
                bot.send_message(CHAT_ID, "MANUAL mode enabled")
            else:
                bot.send_message(CHAT_ID, "MANUAL mode disabled")

async def send_glass_state():
    await asyncio.sleep(5)

    manual_mode_flag = manual_mode_fpath.is_file()

    while True:
        await asyncio.sleep(2)

        # ...

@dp.message(Command('start'))
async def start_cmd(message: Message):
    if not is_private_user(message):
        return

    await message.answer("Welcome! Use /help to see details about bot.")

@dp.message(Command('help'))
async def start_cmd(message: Message):
    if not is_private_user(message):
        return

    await message.answer("I am Smart Glass Puller Bot.\n\nI serve to look for all new reference frames, videos and admin requests.\n\nAvailable commands:\n/start\n/help")

#@dp.message()
#async def any_command(message: Message):
    #await message.answer("Answered by Puller")

async def main():
    await bot.send_message(CHAT_ID, "Puller Bot started.")

    asyncio.create_task(send_temperature())
    asyncio.create_task(send_updated_reference_frames())
    asyncio.create_task(send_videos())
    asyncio.create_task(send_mode())
    asyncio.create_task(send_glass_state())

    await dp.start_polling(bot)
    

if __name__ == '__main__':
    prepare_folders()
    asyncio.run(main())
