import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
from func.discord import MyBot
from func.log import get_log
from typing import Literal
import json

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
    @app_commands.choices(kind=[
        Choice(name="標準", value="1408781349241749556"),
        Choice(name="参加申請", value="1408781349241749561"),
        Choice(name="危険単語", value="1408781349631950848"),
        Choice(name="危険", value="1408781349631950852")
    ])
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
        kind:Choice[str], 
        lang:Literal["JP", "EN", "CN"]
    ):
        try:
            await interaction.response.defer()
            invite = await self.bot.fetch_invite(invite_url)
            resp_json = {
                    "server_id": invite.guild.id,
                    "server_name": invite.guild.name,
                    "tag_name": name,
                    "category": kind.value,
                    "lang": lang
            }
            response = (
                await self.bot.supabase.table("tags")
                .insert(resp_json)
                .execute()
            )
            resp_json_str = json.dumps(resp_json, indent=4, ensure_ascii=False)
            await interaction.followup.send(embed=discord.Embed(
                title="タグ追加",
                description=f"""\
                **データベースに情報を追加しました。**
                ```json
                {resp_json_str}
                ```"""
            ))
        except Exception as e:
            await interaction.followup.send(embed=discord.Embed(
                title="エラー",
                description=f"タグの追加中にエラーが発生しました。\n```{e}```"
            ))
            self.log.error(e)

async def setup(bot):
    await bot.add_cog(ManageTagCog(bot))