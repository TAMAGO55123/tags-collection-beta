import discord
from discord import app_commands
from discord.ext import commands, tasks
from os import getenv
from dotenv import load_dotenv
from supabase import AsyncClient, acreate_client
load_dotenv()

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="tagb_", intents=intents)

