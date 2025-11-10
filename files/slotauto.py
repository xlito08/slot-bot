import discord
from discord.ext import commands,tasks
from datetime import datetime, timedelta
import json
import pytz
from colorama import Fore, Style, Back
from files.view import SlotView1
from fuctions import fuctions as fu
from config import *

class SlotAuto1(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.ping_reset.start()
        
    def cog_unload(self):
        self.ping_reset.stop()

    @tasks.loop(minutes=1)
    async def ping_reset(self):
        current_time = datetime.now(pytz.timezone(TIMEZONE)) 

        if current_time.hour == 23 and current_time.minute == 55:
            try:
                with open("./database/slot.json", "r") as f:
                    data = json.load(f)
            except FileNotFoundError:
                data = []

            for entry in data:
                entry["ping"] = 0
                entry["everyone_ping"] = 0

            with open("./database/slot.json", "w") as f:
                json.dump(data, f, indent=2)
            
            guild = self.bot.get_guild(SERVER_ID)  
            if guild is not None:
                role = guild.get_role(ROLE_ID)  
                if role is not None:
                    chh = self.bot.get_channel(SELLER_CHANNEL)
                    embed = discord.Embed(title="Pings Reset Time", description="All Pings have been reset", color=discord.Color.green())
                    embed.set_footer(text="Slot Automation System By Asbron")
                    embed.timestamp = datetime.now()
                    await chh.send(f"{role.mention}", embed=embed)
                    print(f"{Fore.GREEN}PINGS RESTING{Style.RESET_ALL}")
                else:
                    print("Role not found")
            else:
                print("Guild not found")
        


class SlotAuto2(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.auto_revoke.start()
        
    def cog_unload(self):
        self.auto_revoke.stop()
        
    @tasks.loop(minutes=5)
    async def auto_revoke(self):
        time = datetime.now().date()
        try:
            with open("./database/slot.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []
        
        for entry in data:
            code = entry["time"]
            revoke_time = await fu.decode_special_code(code)
            if time == revoke_time:
                ch = self.bot.get_channel(entry["channel"])
                user = self.bot.get_user(entry["owner"])
                guild = self.bot.get_guild(SERVER_ID)
                role = guild.get_role(ROLE_ID)
                embed = discord.Embed(title="Slot Revoked", description=f"{user.mention}Your slot time has over", color=discord.Color.red())
                embed.add_field(name="", value=f"To Renew contect to Owners", inline=False)
                embed.set_thumbnail(url="https://media.discordapp.net/attachments/1210519710635003915/1211365260439851068/xL0OJde.png?ex=65edeed0&is=65db79d0&hm=9c2fe0bbd36105312b8c25bde91a723930d7a51d726023acacdc4b9da8898b1e&=&format=webp&quality=lossless&width=640&height=640")
                embed.set_footer(text="slot system by Asbron")
                try:
                    await user.send(embed=embed)
                    await user.remove_roles(role)
                except discord.Forbidden:
                    pass
                overwite = discord.PermissionOverwrite(view_channel=True)
                await ch.set_permissions(ch.guild.default_role, overwrite=overwite)
                if user:
                    overwrite_user = discord.PermissionOverwrite(view_channel=False)
                    await ch.set_permissions(user, overwrite=overwrite_user)
                await ch.send(embed=embed, view=SlotView1())
                    
                
                
                
                
async def setup(bot):
    await bot.add_cog(SlotAuto1(bot))
    await bot.add_cog(SlotAuto2(bot))