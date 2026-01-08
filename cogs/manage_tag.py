import discord
from discord.ext import commands
from discord import app_commands, ButtonStyle, HTTPException, NotFound
from discord.app_commands import Choice
from discord.ui import View, button, Button
from func.discord import MyBot
from func.log import get_log
from typing import Literal
import json
import datetime
import math
from os import getenv
from dotenv import load_dotenv
load_dotenv()
from func.db import Tag_DB, Tags, Tag

class Tag_Embed(View):
    def __init__(self, *, pages:list, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.pages:list[Tag] = pages
        self.current_page:int = 0
    
    async def update_message(self, interaction:discord.Interaction):
        a = self.pages[self.current_page]
        embed = discord.Embed(
            title=f"ページ数({self.current_page + 1} / {len(self.pages)})",
            description=f"""\
**タグ** : {a.tag_name}
**サーバー名** : {a.server_name}
**カテゴリ** : {a.category}
**主要言語** : {a.lang}
**招待リンク** : {a.server_invite}
"""
        ).set_thumbnail(url=a.server_icon)
        if self.current_page == 0:
            self.previous.disabled = True
        else:
            self.previous.disabled = False
        if self.current_page == len(self.pages) - 1 :
            self.next.disabled = True
        else:
            self.next.disabled = False
        await interaction.response.edit_message(embed=embed, view=self)
    
    @button(label="◀︎", style=ButtonStyle.secondary)
    async def previous(self, interaction:discord.Interaction, button:Button):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_message(interaction)
        else:
            await interaction.response.defer()
    
    @button(label="▶︎", style=ButtonStyle.secondary)
    async def next(self, interaction:discord.Interaction, button:Button):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await self.update_message(interaction)
        else:
            await interaction.response.defer()
class ManageTagCog(commands.Cog):
    def __init__(self, bot:MyBot):
        self.bot = bot
        self.log = get_log("ManageTagCog")
        self.DB = Tag_DB()
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.log.info(f"ManageTagCogを読み込みました!")

    class tagdb1(app_commands.Group):
        pass

    tagdb = tagdb1(name="btagdb", description="【β】タグに関するコマンド。")
    class tag1(app_commands.Group):
        pass

    tag = tag1(name="btag", description="【β】タグに関するコマンド。")

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
            
            server_icon = invite.guild.icon.url if invite.guild.icon else ""
            
            ok, res = await self.DB.add_tag(
                guild_id=invite.guild.id,
                guild_name=invite.guild.name,
                invite_url=invite.url,
                guild_icon=server_icon,
                tag_name=name,
                category=_kind,
                lang=lang
            )
            if res == "登録済み":
                raise Exception("登録済みです。")
            if ok != True:
                raise Exception(f"データベースエラー:{res}")
            await interaction.followup.send(embed=discord.Embed(
                title="タグ追加",
                description=f"""\
                **データベースに情報を追加しました。**
                ----------------------
                **タグ** : {name}
                **サーバー名** : {invite.guild.name}
                **カテゴリ** : {kind}
                **主要言語** : {lang}
                **招待リンク** : {invite.url}"""
            ).set_thumbnail(url=server_icon))
        except NotFound as e:
            await interaction.followup.send(embed=discord.Embed(
                title="エラー",
                description=f"招待リンクが有効ではありません。\n```{e}```"
            ))
            self.log.error(e)
        except HTTPException as e:
            await interaction.followup.send(embed=discord.Embed(
                title="エラー",
                description=f"招待リンクの取得に失敗しました。\n```{e}```"
            ))
            self.log.error(e)
        except Exception as e:
            await interaction.followup.send(embed=discord.Embed(
                title="エラー",
                description=f"タグの追加中にエラーが発生しました。\n```{e}```"
            ))
            self.log.error(e)
    
    @tag.command(name="list", description="タグのリストを取得します。(取得は50件ごと)")
    @app_commands.describe(
        name="タグの名前",
        category="カテゴリ",
        page="ページ数"
    )
    async def list(
        self,
        interaction:discord.Interaction,
        name:str=None,
        category:Literal["標準", "参加申請", "危険"]=None,
        lang:Literal["Japanese", "English", "Chinese"]=None,
        page:int=1
    ):
        await interaction.response.defer()
        try:
            role_id = 1408781348134719593
            has_role = any(role.id == role_id for role in interaction.user.roles)
            _kind = 0
            match category:
                case "標準":
                    _kind = 0
                case "参加申請":
                    _kind = 1
                case "危険":
                    _kind = 2
                case None:
                    _kind = None
            db:Tags = await self.DB.get_tag(tag_name=name, category=_kind, lang=lang, page=page, has_d=has_role)
            if db:
                view = Tag_Embed(pages=db.data)
                a = db.data[0]
                is_web = False
                webdes = ""
                if a.description == {}:
                    is_web = False
                else:
                    is_web = True
                    webdes = f"\n**サーバー説明**\n{a.description["description"]}"
                embed = discord.Embed(
                    title=f"ページ数({1} / {len(db.data)})",
                    description=f"""\
                    **登録ID** : {a.id}
                    **タグ** : {a.tag_name}
                    **サーバー名** : {a.server_name}
                    **カテゴリ** : {a.category}
                    **主要言語** : {a.lang}
                    **招待リンク** : {a.server_invite}
                    **登録日** : <t:{a.created_at}:f>{webdes}
                    """
                ).set_thumbnail(url=a.server_icon)
                view.previous.disabled = True
                if len(db.data) == 1 :
                    view.next.disabled = True
                await interaction.followup.send(embed=embed, view=view)
            else:
                await interaction.followup.send("タグがありません。")
        except Exception as e:
            await interaction.followup.send(embed=discord.Embed(
                title="エラー",
                description=f"タグの読み込み中にエラーが発生しました。\n```{e}```"
            ))
            self.log.error(e)
    
    @tagdb.command(name="delete", description="タグを削除します")
    @app_commands.describe(
        id="管理ID"
    )
    async def delete(self, interaction:discord.Interaction, id:int):
        await interaction.response.defer()
        try:
            ok, res = self.DB.delete_tag(id)
            if ok != True:
                raise Exception(f"データベースエラー : {res}")
            await interaction.followup.send(embed=discord.Embed(
                title="タグ削除",
                description="タグを削除しました。"
            ))
        except Exception as e:
            await interaction.followup.send(embed=discord.Embed(
                title="エラー",
                description=f"タグの削除中にエラーが発生しました。\n```{e}```"
            ))
            self.log.error(e)
    
    @tagdb.command(name="name", description="タグの名前を変更します。")
    @app_commands.describe(
        id="管理ID",
        name="新しいタグの名前"
    )
    async def name(self, interaction:discord.Interaction, id:int, name:str):
        await interaction.response.defer()
        try:
            db:Tags = self.DB.get_tag(id=id)
            if db.count == 0:
                raise Exception("タグを取得できませんでした。")
            
            invite:discord.Invite = self.bot.fetch_invite(db.data[0].server_invite)
            server_name = invite.guild.name
            server_icon = invite.guild.icon
            ok, res = self.DB.edit_tag(
                tag_id=id,
                tag_name=name,
                server_name=server_name,
                server_icon=server_icon
            )
            if ok != True:
                raise Exception(f"データベースエラー : {res}")
            await interaction.followup.send(embed=discord.Embed(
                title="タグ名変更",
                description="タグの名前を変更し、サーバー名とアイコンも更新しました。"
            ))
        except NotFound as e:
            await interaction.followup.send(embed=discord.Embed(
                title="エラー",
                description=f"保存した招待リンクが有効ではないため、タグを削除します。\n```{e}```"
            ))
            self.log.error(e)
            try:
                db:Tags = self.DB.get_tag(id=id)
                if db.count == 0:
                    raise Exception("タグを取得できませんでした。")
                ok, res = self.DB.delete_tag(db.data[0].id)
                if ok != True:
                    raise Exception(f"データベースエラー : {res}")
                await interaction.followup.send(embed=discord.Embed(
                    title="タグ削除",
                    description="タグを削除しました。"
                ))
            except Exception as e:
                await interaction.followup.send(embed=discord.Embed(
                    title="エラー",
                    description=f"タグの削除中にエラーが発生しました。\n```{e}```"
                ))
                self.log.error(e)
        except Exception as e:
            await interaction.followup.send(embed=discord.Embed(
                title="エラー",
                description=f"タグの追加中にエラーが発生しました。\n```{e}```"
            ))
            self.log.error(e)

    @tagdb.command(name="invite", description="タグの招待を変更します。")
    @app_commands.describe(
        id="管理ID",
        name="新しい招待リンク"
    )
    async def name(self, interaction:discord.Interaction, id:int, invite_url:str):
        await interaction.response.defer()
        try:
            db:Tags = self.DB.get_tag(id=id)
            if db.count == 0:
                raise Exception("タグを取得できませんでした。")
            
            invite:discord.Invite = self.bot.fetch_invite(invite_url)
            server_name = invite.guild.name
            server_icon = invite.guild.icon
            ok, res = self.DB.edit_tag(
                tag_id=id,
                server_name=server_name,
                server_icon=server_icon,
                server_invite=invite_url
            )
            if ok != True:
                raise Exception(f"データベースエラー : {res}")
            await interaction.followup.send(embed=discord.Embed(
                title="タグ名変更",
                description="タグの招待を変更し、サーバー名とアイコンも更新しました。"
            ))
        except NotFound as e:
            await interaction.followup.send(embed=discord.Embed(
                title="エラー",
                description=f"保存した招待リンクが有効ではないため、タグを削除します。\n```{e}```"
            ))
            self.log.error(e)
            try:
                db:Tags = self.DB.get_tag(id=id)
                if db.count == 0:
                    raise Exception("タグを取得できませんでした。")
                ok, res = self.DB.delete_tag(db.data[0].id)
                if ok != True:
                    raise Exception(f"データベースエラー : {res}")
                await interaction.followup.send(embed=discord.Embed(
                    title="タグ削除",
                    description="タグを削除しました。"
                ))
            except Exception as e:
                await interaction.followup.send(embed=discord.Embed(
                    title="エラー",
                    description=f"タグの削除中にエラーが発生しました。\n```{e}```"
                ))
                self.log.error(e)
        except Exception as e:
            await interaction.followup.send(embed=discord.Embed(
                title="エラー",
                description=f"タグの追加中にエラーが発生しました。\n```{e}```"
            ))
            self.log.error(e)

async def setup(bot):
    await bot.add_cog(ManageTagCog(bot))