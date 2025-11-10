import discord
from discord.ext import commands,tasks
from discord import app_commands
import json
from files.view import SlotView1
from fuctions import fuctions as fu
from config import *

import json

async def get_categories():
    try:
        with open("./database/setup.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        return []  

    ids = [entry["category"] for entry in data]
    return ids

async def get_all_channels(guild):
    try:
        with open("./database/slot.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []
    channels = [entry["channel"] for entry in data if guild.get_channel(entry["channel"])]
    return channels

    

class Ping(commands.Cog):
    def __init__(self,bot):
        self.bot = bot 
      
  
    
    @commands.Cog.listener()
    async def on_message(self,message):
        if message.author.bot:
            return
        if isinstance(message.channel, discord.DMChannel):
            return
        if message.channel.category_id:
            list_ids = SlOT_CATEGORYS
            channels = await get_all_channels(message.guild)
            if message.channel.category_id in list_ids and message.channel.id in channels:
               
                if '@here' in message.content:
                    try:
                        with open("./database/slot.json", "r") as f:
                            data = json.load(f)
                    except FileNotFoundError:
                        data = []
                    for entry in data:
                        if entry["channel"] == message.channel.id:
                                entry["ping"] += 1
                                with open("./database/slot.json", "w") as f:
                                    json.dump(data,f,indent=4)
                                left = entry["ping_limit"] - entry["ping"]
                                Ping_limit = entry["ping_limit"]
                                Ping_here = entry["ping"]
                                msd = f"**{Ping_here}/{Ping_limit} | USE MM**"
                                await message.channel.send(msd)
                                if entry["ping"] > entry["ping_limit"]:
                                    user = message.guild.get_member(entry["owner"])
                                    overwrite = discord.PermissionOverwrite()
                                    overwrite.send_messages = False
                                    await message.channel.set_permissions(user,overwrite=overwrite)
                                    revokeembed = discord.Embed(title="Channel Revoked",description=f"Your channel has been revoked due to excessive pings",color=discord.Color.red())
                                    await message.channel.send(embed=revokeembed,view=SlotView1())
                                    return
                elif '@everyone' in message.content:
                    try:
                        with open("./database/slot.json", "r") as f:
                            data = json.load(f)
                    except FileNotFoundError:
                        data = []
                    for entry in data:
                        if entry["channel"] == message.channel.id:
                                entry["everyone_ping"] += 1
                                with open("./database/slot.json", "w") as f:
                                    json.dump(data,f,indent=4)
                                left = entry["everyone_ping_limit"] - entry["everyone_ping"]
                                every_one_ping = entry["everyone_ping"]
                                everyone_ping_limit = entry["everyone_ping_limit"]
                                msdd = f"**{every_one_ping}/{everyone_ping_limit} | USE MM**"
                                await message.channel.send(msdd)
                                if entry["everyone_ping"] > entry["everyone_ping_limit"]:
                                    user = message.guild.get_member(entry["owner"])
                                    overwrite = discord.PermissionOverwrite()
                                    overwrite.send_messages = False
                                    await message.channel.set_permissions(user,overwrite=overwrite)
                                    revokeembed = discord.Embed(title="Channel Revoked",description=f"Your channel has been revoked due to excessive pings",color=discord.Color.red())
                                    await message.channel.send(embed=revokeembed,view=SlotView1())
                                    return
                else:
                    pass
            else:
                pass
        else:
            pass
        
                                
                              
                        
                                
                                
                            
                        

                    

async def setup(bot):
    await bot.add_cog(Ping(bot))
                
            