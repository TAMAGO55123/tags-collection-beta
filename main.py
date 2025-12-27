from func.log import get_log, stream_handler
import asyncio
import discord
from discord import app_commands
from discord.ext import commands, tasks
from func.discord import MyBot
from os import getenv
from dotenv import load_dotenv
from supabase import AsyncClient, acreate_client
load_dotenv()

intents = discord.Intents.all()

bot = MyBot(command_prefix="tagb_", intents=intents)

TOKEN = getenv("TOKEN")
SUPABASE_URL: str = getenv("SUPABASE_URL")
SUPABASE_ANON_KEY: str = get("SUPABASE_ANON_KEY")

main_log = get_log("Main")

console_task = None

async def console_input():
    while True:
        line = await aioconsole.ainput("type:")
        if line.strip() == "finish":
            await bot_stop()
            break
async def bot_stop():
    main_log.info("Stop.")
    await bot.close()

async def main(bot:MyBot):
    log = main_log
    try:
        bot.supabase = await acreate_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        @bot.event
        async def on_ready():
            global console_task
            console_task = asyncio.create_task(console_input())
            log.info(f"{bot.user}としてログインしました^o^")
        await bot.start(TOKEN)
    except Exception as e:
        log.error(f"BOTの起動中にエラーが発生しました\n{e}")
        
