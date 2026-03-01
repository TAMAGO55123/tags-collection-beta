from discord.ext import commands
from supabase import AsyncClient
from cloudflare import AsyncCloudflare

class MyBot(commands.Bot):
    def __init__(self, **options):
        super().__init__(**options)
        self.cf: AsyncCloudflare = None