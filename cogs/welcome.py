import discord
from discord.ext import commands
from discord import app_commands
from func.discord import MyBot
from func.db import Tag_DB
from func.log import get_log

class WelcomeCog(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.log = get_log("ManageTagCog")
        self.DB = Tag_DB()
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.log.info(f"SampleCogを読み込みました!")
    
    @commands.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        join_channel = member.guild.get_channel(1408781348616933487)
        verify_channel = member.guild.get_channel(1408781348616933488)
        
        await join_channel.send(content=f"""# Welcome to Server!
Joined <@{member.id}> ({member.name})
Now members: {member.guild.member_count - 1} -> {member.guild.member_count}""")
        msg = await verify_channel.send(content=f"<@{member.id}>")
        await msg.delete()
    
    @commands.Cog.listener()
    async def on_member_remove(self, member:discord.Member):
        join_channel = member.guild.get_channel(1408781348616933487)
        
        await join_channel.send(content=f"""User Left...
Left <@{member.id}> ({member.name})
Now members: {member.guild.member_count + 1} -> {member.guild.member_count}
""")

async def setup(bot):
    # await bot.add_cog(WelcomeCog(bot))
    pass