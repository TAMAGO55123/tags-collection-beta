import aiohttp
from os import getenv
from dotenv import load_dotenv
load_dotenv()
from typing import Tuple, Union

API_URL = getenv("API_URL")
API_KEY = getenv("API_KEY")

async def add_tag(guild_id:int, guild_name:str, invite_url:str, guild_icon:str, tag_name: str, category: int, lang: str) -> Tuple[bool, Union[dict, str]]:
    """
    Cloudflare Workers の /tags API にタグを登録する関数
    """

    payload = {
        "server_id": str(guild_id),
        "server_name": guild_name,
        "server_invite": invite_url,
        "server_icon": guild_icon,
        "tag_name": tag_name,
        "category": category,
        "lang": lang
    }

    header = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, json=payload, headers=header) as resp:
            if resp.status == 200:
                return True, await resp.json()
            else:
                return False, await resp.text()
