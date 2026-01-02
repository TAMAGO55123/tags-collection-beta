import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
from func.discord import MyBot
from func.log import get_log
from typing import Literal
import json
import datetime
import math
from os import getenv
from dotenv import load_dotenv
load_dotenv()
from func.db import add_tag
class ManageTagCog(commands.Cog):
    def __init__(self, bot:MyBot):
        self.bot = bot
        self.log = get_log("ManageTagCog")
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.log.info(f"ManageTagCogを読み込みました!")

    class tagdb1(app_commands.Group):
        pass

    tagdb = tagdb1(name="btag", description="【β】タグに関するコマンド。")

    @tagdb.command(name="add", description="【β】タグを追加します。")
    @app_commands.describe(
        name="タグの名前",
        invite_url="サーバーの招待リンク(あればバニティURLとか)",
        kind="タグの種類(選んでね)",
        lang="タグサーバーの主言語(選んでね)"
    )
    async def add(
        self,
        interaction:discord.Interaction, 
        name:str, 
        invite_url:str, 
        kind:Literal["標準", "参加申請", "危険"], 
        lang:Literal["Japanese", "English", "Chinese"]
    ):
        try:
            _kind = 0
            match kind:
                case "標準":
                    _kind = 0
                case "参加申請":
                    _kind = 1
                case "危険":
                    _kind = 2
            await interaction.response.defer()
            invite = await self.bot.fetch_invite(invite_url)
            if invite.type != discord.InviteType.guild:
                raise Exception("指定されたURLはサーバー招待ではありません。")
            if "GUILD_TAGS" not in invite.guild.features:
                raise Exception("指定された招待リンクのサーバーはギルドタグを持っていないようです。")
            if invite.expires_at != None:
                raise Exception("指定されたURLの期限は無限ではありません。")
            if invite is None:
                raise Exception("招待リンクの情報の取得に失敗しました。")
            
            server_icon = invite.guild.icon.url if invite.guild.icon else ""
            
            ok, res = await add_tag(
                guild_id=invite.guild.id,
                guild_name=invite.guild.name,
                invite_url=invite.url,
                guild_icon=server_icon,
                tag_name=name,
                category=_kind,
                lang=lang
            )
            if ok != True:
                raise Exception(f"データベースエラー:{res}")
            await interaction.followup.send(embed=discord.Embed(
                title="タグ追加",
                description=f"""\
                **データベースに情報を追加しました。**"""
            ))
        except Exception as e:
            await interaction.followup.send(embed=discord.Embed(
                title="エラー",
                description=f"タグの追加中にエラーが発生しました。\n```{e}```"
            ))
            self.log.error(e)

async def setup(bot):
    await bot.add_cog(ManageTagCog(bot))