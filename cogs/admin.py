import discord
from discord.ext import commands
from discord import app_commands
from func.discord import MyBot
from func.db import Tag_DB
from func.log import get_log

class SendModal(discord.ui.Modal):
    def __init__(self, channel:discord.TextChannel, ifembed:bool,user:discord.Member):
        super().__init__(
            title="フォーム",
            timeout=None,
        )

        self.messages = discord.ui.TextInput(
            label="メッセージ",
            style=discord.TextStyle.paragraph,
            required=True,
        )
        self.add_item(self.messages)

        self.channel = channel
        self.ifembed = ifembed
        self.user = user

    async def on_submit(self, interaction:discord.Interaction):
        if self.ifembed:
            a = await self.channel.send(embed=discord.Embed(description=self.messages))
        else:
            a = await self.channel.send(content=self.messages)
        await interaction.response.send_message("sended.",ephemeral=True)

class AdminCog(commands.Cog):
    def __init__(self, bot:MyBot):
        self.bot = bot
        self.log = get_log("TagCog")
        self.DB = Tag_DB()
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.log.info(f"AdminCogを読み込みました!")
    
    class admin1(app_commands.Group):
        pass
    
    admin = admin1(name="admin", description="管理者専用コマンド", default_permissions=discord.Permissions(administrator=True))

    @admin.command(name="send", description="送信")
    async def send(self, interaction:discord.Interaction, channel:discord.TextChannel = None, ifembed:bool = True):
            if channel == None:
                send_channel = interaction.channel
            else:
                send_channel = channel
            modal = SendModal(channel=send_channel,ifembed=ifembed,user=interaction.user)
            await interaction.response.send_modal(modal)

async def setup(bot):
    await bot.add_cog(AdminCog(bot))