from func.log import get_log, stream_handler
import asyncio
import discord
from discord import app_commands
from discord.ext import commands, tasks
from func.discord import MyBot
from os import getenv, listdir
from dotenv import load_dotenv
from supabase import AsyncClient, acreate_client
from cloudflare import AsyncCloudflare
import aioconsole
load_dotenv()

intents = discord.Intents.all()

bot = MyBot(command_prefix="tagb_", intents=intents)

TOKEN = getenv("TOKEN")
SUPABASE_URL: str = getenv("SUPABASE_URL")
SUPABASE_ANON_KEY: str = getenv("SUPABASE_ANON_KEY")
SUPABASE_NAME: str = getenv("SUPABASE_USER")
SUPABASE_PASS: str = getenv("SUPABASE_PASS")

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
        bot.cf = AsyncCloudflare(
            api_token = getenv("CLOUDFLARE_API_TOKEN")
        )

        @bot.event
        async def on_ready():
            global console_task
            console_task = asyncio.create_task(console_input())
            log.info(f"{bot.user}としてログインしました^o^")
        @bot.event
        async def setup_hook():
            try:
                for cog in listdir("cogs"):
                    if cog.endswith(".py"):
                        await bot.load_extension(f"cogs.{cog[:-3]}")
                synced = await bot.tree.sync()
                log.info(f"{len(synced)}個のコマンドを同期しました。")
            except Exception as e:
                log.error(f"コマンドの同期中にエラーが発生しました。")

        await bot.start(TOKEN)
    except Exception as e:
        log.error(f"BOTの起動中にエラーが発生しました\n{e}")
        
try:
    discord.utils.setup_logging(handler=stream_handler)
    asyncio.run(main(bot=bot))
except Exception as e:
    print(f'エラーが発生しました: {e}')