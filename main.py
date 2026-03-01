from func.log import get_log, stream_handler
import asyncio
import discord
from discord import app_commands
from discord.ext import commands, tasks
from func.discord import MyBot
from os import getenv, listdir
from dotenv import load_dotenv
import aioconsole
from datetime import datetime
import math
load_dotenv()

intents = discord.Intents.all()

bot = MyBot(command_prefix="tagb_", intents=intents)

TOKEN = getenv("TOKEN")

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
        @bot.event
        async def on_ready():
            global console_task
            console_task = asyncio.create_task(console_input())
            log.info(f"{bot.user}としてログインしました^o^")
            log_channel = bot.get_channel(1408781350819069955)
            await log_channel.send(embed=discord.Embed(
                title="BOTが起動しました^p^",
                description="BOTが起動しました",
            ))
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
        
        class SendEmbedModal(discord.ui.Modal):
            def __init__(self, channel:discord.TextChannel, message:str):
                super().__init__(
                    title="フォーム",
                    timeout=None,
                )

                self.messages = discord.ui.TextInput(
                    label="Color Code",
                    style=discord.TextStyle.short,
                    max_length=6,
                    required=False,
                )
                self.add_item(self.messages)

                self.channel = channel
                self.message = message

            async def on_submit(self, interaction:discord.Interaction):
                if self.messages.value:
                    a = int(f"0x{self.messages.value}", 16)
                else:
                    a = None
                await self.channel.send(embed=discord.Embed(description=self.message, color=a))
                await interaction.response.send_message("sended.",ephemeral=True)
        
        @bot.tree.context_menu(name="メッセージを再送信")
        @app_commands.default_permissions(administrator=True)
        async def message_re_send(interaction:discord.Interaction, message:discord.Message):
            await message.channel.send(content=message.content, embeds=message.embeds)
            await interaction.response.send_message(content="sended.",ephemeral=True)

        @bot.tree.context_menu(name="メッセージを埋め込みに変換")
        @app_commands.default_permissions(administrator=True)
        async def message_send_embed(interaction:discord.Interaction, message:discord.Message):
            modal = SendEmbedModal(channel=message.channel, message=message.content)
            await interaction.response.send_modal(modal)
            

        await bot.start(TOKEN)
    except Exception as e:
        log.error(f"BOTの起動中にエラーが発生しました\n{e}")
        
try:
    discord.utils.setup_logging(handler=stream_handler)
    asyncio.run(main(bot=bot))
except Exception as e:
    print(f'エラーが発生しました: {e}')