import discord
from discord.ext import commands,tasks
import json
import asyncio
from fuctions import fuctions as fu
from config import *

class SlotView1(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.button(label="ReOpen", style=discord.ButtonStyle.green, custom_id="reopen")
    async def reopen(self,click: discord.Interaction, button: discord.ui.Button):
        await click.response.defer(ephemeral=True)
        if not click.user.guild_permissions.administrator:
            return await click.followup.send("You are not allowed to do this", ephemeral=True)
        try:
            msg = await click.followup.send("Reopening.......", ephemeral=True)
            try:
                with open("./database/slot.json", "r") as f:
                    data = json.load(f)
            except FileNotFoundError:
                data = []
            for entry in data:
                user = click.guild.get_member(entry["owner"])
                ch = entry["channel"]
                if click.channel_id == ch:
                    
                    time = await fu.decode_special_code(entry["time"])
                    
                    embed = discord.Embed(title="Slot Reopened", color=discord.Color.green())
                    response = [
                        f"Slot has been reopened by {click.user.name}",
                        f"{user.mention} Your can start using the slot again",
                        f"Slot will be closed at {time}"
                    ]
                    embed.description = "\n".join(response)
                    embed.set_thumbnail(url="https://media.discordapp.net/attachments/1210519710635003915/1211365941674254346/hMQOujZ.png?ex=65edef72&is=65db7a72&hm=74631e0a5ca194d98d3723d6ecb04ae30535d2b4552beacf1833bd25ce649e6e&=&format=webp&quality=lossless&width=640&height=640")
                    chh = click.channel
                    await click.followup.edit_message(message_id=msg.id, content="Giving permission to user and reopening slot.......")
                    await asyncio.sleep(3)
                    await chh.set_permissions(user, send_messages=True)
                    await asyncio.sleep(3)  
                    await click.followup.edit_message(message_id=msg.id, content="Resetting the pings.......")
                    await asyncio.sleep(3)
                    try:
                        guid = click.guild
                        role = guid.get_role(ROLE_ID)
                        await user.add_roles(role)
                    except discord.Forbidden:
                        pass
                    entry["ping"] = 0
                    entry["everyone_ping"] = 0
                    with open("./database/slot.json", "w") as f:
                        json.dump(data, f, indent=2)
                    await chh.send(embed=embed)
                    try:
                        await user.send(embed=embed)
                    except discord.Forbidden:
                        pass
                    await click.followup.edit_message(message_id=msg.id, content="Slot has been reopened")
                    await click.message.delete()
                    return
        except Exception as e:
            print(e)
            await click.edit_original_response(content="An error occured")
            return

    @discord.ui.button(label='Delete', style=discord.ButtonStyle.red, custom_id="delete")
    async def delete(self,click: discord.Interaction, button: discord.ui.Button):
        await click.response.send_message("Deleting.......", ephemeral=True)
        await click.original_response()
        if not click.user.guild_permissions.administrator:
            return await click.followup.send("You are not allowed to do this", ephemeral=True)
        try:
            try:
                with open("./database/slot.json", "r") as f:
                    data = json.load(f)
            except FileNotFoundError:
                data = []
            for entry in data:
                channel = entry["channel"]
                if click.channel_id == channel:
                    data.remove(entry)
                    with open("./database/slot.json", "w") as f:
                        json.dump(data, f, indent=2)
                    await click.edit_original_response(content="Slot has been set in delete list .Wil be deleted in 5 sec")
                    await asyncio.sleep(5)
                    await click.channel.delete()
                    return
        except Exception as e:
            print(e)
            await click.followup.send("An error occured", ephemeral=True)
            return

async def setup(bot):
    await bot.add_cog(SlotView1(bot))
    