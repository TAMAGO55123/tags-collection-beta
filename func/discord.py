from discord.ext import commands
from supabase import AsyncClient

class MyBot(commands.Bot):
    def __init__(self, **options):
        super().__init__(**options)
        self.supabase:AsyncClient = None
        self.supabase_session = None