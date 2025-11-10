import discord
from discord.ext import commands,tasks
from discord import app_commands
import json
from datetime import datetime, timedelta
from files.view import SlotView1
from config import *
import pytz 
import asyncio
from fuctions import fuctions as fu

class Slot(commands.Cog):
    def __init__(self,bot):
        self.bot = bot 
      

    @app_commands.command(name="create-slot", description="Create a slot")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.choices(
        time=[
            app_commands.Choice(name="3 days", value=3),
            app_commands.Choice(name="Weekly", value=7),
            app_commands.Choice(name="15 days", value=15),
            app_commands.Choice(name="Monthly", value=30),
            app_commands.Choice(name="Yearly", value=365),
        ],
        slot_category=[
            app_commands.Choice(name="Category 1", value=1),
            app_commands.Choice(name="Category 2", value=2),
            app_commands.Choice(name="Category 3", value=3),
        ],
    )
    async def create_slot(
        self,
        inter: discord.Interaction,
        time: app_commands.Choice[int],
        slot_category: app_commands.Choice[int],
        slot_owner: discord.Member,
        here_ping_limit: int = 3,
        everyone_ping_limit: int = 0,
    ):
        await inter.response.defer(ephemeral=True)
        guild = inter.guild_id

        try:
            with open("./database/slot.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []

        try:
            role = discord.utils.get(inter.guild.roles, id=ROLE_ID)
            if role is not None:
                await slot_owner.add_roles(role)
        except Exception as e:
            print(e)

        existing_id = [
            entry for entry in data if entry["owner"] == slot_owner.id and entry["guild_id"] == guild
        ]
        if existing_id:
            await inter.followup.send(f"Slot already created for {slot_owner.mention}", ephemeral=True)
            return

        try:
            if time.value == 3:
                time_revok = datetime.now() + timedelta(days=3)
            elif time.value == 7:
                time_revok = datetime.now() + timedelta(days=7)
            elif time.value == 15:
                time_revok = datetime.now() + timedelta(days=15)
            elif time.value == 30:
                time_revok = datetime.now() + timedelta(days=30)
            elif time.value == 365:
                time_revok = datetime.now() + timedelta(days=365)

            code = await fu.generate_special_code(time.value)
            recover_code = await fu.recovery_code_gen()

            if slot_category.value == 1:
                category_name = "Category 1"
                category_id = SlOT_CATEGORY_1
            elif slot_category.value == 2:
                category_name = "Category 2"
                category_id = SlOT_CATEGORY_2
            elif slot_category.value == 3:
                category_name = "Category 3"
                category_id = SlOT_CATEGORY_3

            category = discord.utils.get(inter.guild.categories, id=category_id)
            if category is None:
                try:
                    category = await inter.guild.fetch_channel(category_id)
                except discord.NotFound:
                    await inter.followup.send("Error: Category not found", ephemeral=True)
                    return
                except discord.Forbidden as e:
                    print(e)
                    await inter.followup.send("Error: Bot lacks permissions to fetch the category", ephemeral=True)
                    return
                except Exception as e:
                    await inter.followup.send(f"An unexpected error occurred: {e}", ephemeral=True)
                    return

            permissions = category.permissions_for(inter.guild.me)
            if not permissions.manage_channels:
                await inter.followup.send("Error: Bot lacks permissions to manage channels in this category", ephemeral=True)
                return
            if not permissions.view_channel:
                await inter.followup.send("Error: Bot lacks permissions to view this category", ephemeral=True)
                return

            overwrites = {
                inter.guild.default_role: discord.PermissionOverwrite(send_messages=False),
                slot_owner: discord.PermissionOverwrite(send_messages=True),
            }

            ch = await category.create_text_channel(f"{slot_owner.name}-slot", overwrites=overwrites)
            rule_ch = discord.utils.get(inter.guild.text_channels, id=RULE_CHANNEL_ID)
            embed = discord.Embed(title="Slot Details", color=discord.Color.blurple())
            embed.set_author(name=f"{time.name} Slot")
            stap = f"<t:{int(time_revok.timestamp())}:R>"
            msdd = [
                f"**Purchased At:**\n <t:{int(datetime.now().timestamp())}:R>",
                f"**Duration:**\n{time.name}",
                f"**Expires At:**\n{stap}",
                "**Slot Permissions:**",
                f"```{here_ping_limit}x @here pings\n{everyone_ping_limit}x @everyone pings```",
                f"**Category:**\n{category_name}",
                f"**Must Follow {rule_ch.mention}**",
            ]
            embed.set_image(url=EMBED_IMG_URL)
            embed.description = "\n".join(msdd)
            embed.set_footer(text=f"Slot created by {inter.user.name}")
            embed.timestamp = datetime.now()
            if slot_owner.avatar is None:
                embed.set_thumbnail(url=slot_owner.default_avatar.url)
            else:
                embed.set_thumbnail(url=slot_owner.avatar.url)

            embed.set_footer(text="Slot system by Asbron")
            await ch.send(embed=embed, content=slot_owner.mention)

            userembed = discord.Embed(title="Slot Information📃", color=discord.Color.green())
            msg = [
                f"Slot Created for you",
                f"Slot Duration: {time.name}",
                f"Slot Ending: {stap}",
                f"if you lost access to the slot use this code to recover the slot ```{recover_code}```",
                f"Here Ping Limit: {here_ping_limit}",
                f"Everyone Ping Limit: {everyone_ping_limit}",
            ]
            userembed.description = "\n".join(msg)
            try:
                await slot_owner.send(embed=userembed)
            except discord.Forbidden:
                pass

            entry = {
                "owner": slot_owner.id,
                "time": code,
                "channel": ch.id,
                "guild_id": guild,
                "ping": 0,
                "ping_limit": here_ping_limit,
                "everyone_ping": 0,
                "everyone_ping_limit": everyone_ping_limit,
                "recovery_code": recover_code,
            }
            try:
                with open("./database/slot.json", "r") as f:
                    data = json.load(f)
            except FileNotFoundError:
                data = []
            data.append(entry)
            with open("./database/slot.json", "w") as f:
                json.dump(data, f, indent=2)

            await inter.followup.send(embed=discord.Embed(description=f"Slot created for {slot_owner.mention}\n for {time.value} days \n at {ch.mention}"), ephemeral=True)

        except Exception as e:
            await inter.followup.send(f"Error: {e}", ephemeral=True)

            
    @app_commands.command(name="delete-slot", description="Delete a slot")
    @app_commands.checks.has_permissions(administrator=True)
    async def delete_slot(self, inter: discord.Interaction, slot_owner: discord.Member):
        await inter.response.defer(ephemeral=True)
        try:
            with open("./database/slot.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []
        slot_found = False  
        for entry in data:
            if entry["owner"] == slot_owner.id:
                channel = inter.guild.get_channel(entry["channel"])
                await channel.delete()
                data.remove(entry)
                with open("./database/slot.json", "w") as f:
                    json.dump(data, f, indent=2)
                try:
                    role = discord.utils.get(inter.guild.roles, id=ROLE_ID)
                    if role is None:
                        pass 
                    else:
                        await slot_owner.remove_roles(role)
                except Exception as e:
                    print(e)
                    pass    
                
                await inter.followup.send(embed=discord.Embed(description=f"Slot deleted for {slot_owner.mention}"), ephemeral=True)
                slot_found = True
                break
        if not slot_found:
            await inter.followup.send("Slot not found for the user", ephemeral=True)
            return

     
    @app_commands.command(name="hold", description="hold slot")
    @app_commands.checks.has_permissions(administrator=True)
    async def hold_slot(self, inter: discord.Interaction, slot_owner: discord.Member):
        await inter.response.defer(ephemeral=True)
        try:
            with open("./database/slot.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []
        slot_found = False
        for entry in data:
            if entry["owner"] == slot_owner.id:
                await inter.followup.send(embed=discord.Embed(description=f"Holding..............."), ephemeral=True)
                ch = inter.guild.get_channel(entry["channel"])
                overwrite_user = discord.PermissionOverwrite(view_channel=True, send_messages=False)
                await ch.set_permissions(slot_owner, overwrite=overwrite_user)
                embed = discord.Embed(title="SLOT ON HOLD 🛑", color=discord.Color.red())
                respnse = [
                    f"A Report has been filed against {slot_owner.mention} slot",
                    "**Please Don't deal with them until the slot open**",
                ]
                embed.description = "\n".join(respnse)
                embed.set_thumbnail(url="https://media.discordapp.net/attachments/1210519710635003915/1211364205605687358/9oxvYqI.png?ex=65ededd4&is=65db78d4&hm=9fa9fce73f63a72b034597a20cbed6daa20adb5308c57cddfae56683a896be48&=&format=webp&quality=lossless&width=640&height=640")
                embed.set_footer(text=f"Slot Holded by {inter.user.name}",icon_url=inter.user.avatar.url)
                await ch.send(embed=embed)
                try:
                    await slot_owner.send(embed=embed)
                except discord.Forbidden:
                    pass
                await inter.followup.send(embed=discord.Embed(description=f"Slot of {slot_owner.mention} is now holded"), ephemeral=True)
                slot_found = True
                break
        if not slot_found:
            await inter.followup.send("Slot not found for the user", ephemeral=True)
            return


    @app_commands.command(name="revoke", description="revoke a slot")
    @app_commands.checks.has_permissions(administrator=True)
    async def revoke_slot(self, inter: discord.Interaction, slot_owner: discord.Member,reason: str = "No reason provided"):
        await inter.response.defer(ephemeral=True)
        try:
            with open("./database/slot.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []
        slot_found = False  
        for entry in data:
            if entry["owner"] == slot_owner.id:
                channel = inter.guild.get_channel(entry["channel"])
                owverwrite = discord.PermissionOverwrite(send_messages=False)
                await channel.set_permissions(slot_owner, overwrite=owverwrite)
                embed = discord.Embed(title="Slot Revoked 🛑", color=discord.Color.red())
                reponse = [
                    f"Your slot has been revoked by {inter.user.name}",
                    f"Reason: {reason}",
                    f"Please avoid dealing with {slot_owner.mention} until the slot is open again"
                ]
                embed.description = "\n".join(reponse)
                embed.set_footer(text=f"Slot Revoked by {inter.user.name}",icon_url=inter.user.avatar.url)
                embed.set_thumbnail(url="https://media.discordapp.net/attachments/1210519710635003915/1211365260439851068/xL0OJde.png?ex=65edeed0&is=65db79d0&hm=9c2fe0bbd36105312b8c25bde91a723930d7a51d726023acacdc4b9da8898b1e&=&format=webp&quality=lossless&width=640&height=640")
                await channel.send(f"{slot_owner.mention}",embed=embed,view=SlotView1())
                try:
                    role = discord.utils.get(inter.guild.roles, id=ROLE_ID)
                    if role is None:
                        pass 
                    else:
                        await slot_owner.remove_roles(role)
                except Exception as e:
                    print(e)
                    pass
                await inter.followup.send(embed=discord.Embed(description=f"Slot of {slot_owner.mention} is now revoked"), ephemeral=True)
                
                slot_found = True
                break
        if not slot_found:
            await inter.followup.send("Slot not found for the user", ephemeral=True)
            return
                


    @app_commands.command(name="unhold", description="unhold a slot")
    @app_commands.checks.has_permissions(administrator=True)
    async def unhold_slot(self, inter: discord.Interaction, slot_owner: discord.Member):
        await inter.response.defer(ephemeral=True)
        try:
            with open("./database/slot.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []
        slot_found = False  
        for entry in data:
            if entry["owner"] == slot_owner.id:
                overwrite = discord.PermissionOverwrite(view_channel=True, send_messages=False)
                ch_id = entry["channel"]
                ch = inter.guild.get_channel(ch_id)
                await ch.set_permissions(inter.guild.default_role, overwrite=overwrite)
                overwrite_user = discord.PermissionOverwrite(view_channel=True, send_messages=True)
                await ch.set_permissions(slot_owner, overwrite=overwrite_user)
                embed = discord.Embed(title="Slot is UnHolded now 🟢", color=discord.Color.green())
                respone = [
                    f"Slot of {slot_owner.mention} is now unholded",
                    "Report against them has been removed",
                    "You can now deal with them"
                ]
                embed.description = "\n".join(respone)
                embed.set_footer(text=f"Slot UnHolded by {inter.user.name}",icon_url=inter.user.avatar.url)
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1210519710635003915/1211365941674254346/hMQOujZ.png?ex=65edef72&is=65db7a72&hm=74631e0a5ca194d98d3723d6ecb04ae30535d2b4552beacf1833bd25ce649e6e&")
                await ch.send(embed=embed)
                await inter.followup.send(embed=discord.Embed(description=f"Slot of {slot_owner.mention} is now unholded"), ephemeral=True)
                slot_found = True
                break
    
        if not slot_found:
            await inter.followup.send("Slot not found for the user", ephemeral=True)
            return


    @commands.command(name="nuke")
    @commands.has_role(ROLE_ID)
    async def nuke(self, ctx):
        try:
            with open("./database/slot.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []
        owner_found = False
        for i in data:
            if i["owner"] == ctx.author.id:
                channel = ctx.guild.get_channel(i["channel"])
                owner_found = True
                break
        if not owner_found:
            return await ctx.send("You don't have a slot")
        if not channel:
            return await ctx.send("Channel not found.")

        category = channel.category
        position = channel.position

        recent_message = None
        async for message in channel.history(limit=None, oldest_first=True):  
            if message.author.bot:
                recent_message = message
                break

        if not recent_message:
            return await ctx.send("No non-bot messages found in the channel history.")

        await channel.delete()

        recreated_channel = await ctx.guild.create_text_channel(name=channel.name, category=category, position=position)
        
        try:
            with open("./database/slot.json", "r") as f:
                d = json.load(f)
        except FileNotFoundError:
            d = []
        for dd in d:
            dd["channel"] = recreated_channel.id
        with open("./database/slot.json", "w") as f:
            json.dump(d, f, indent=2)
        if recent_message.embeds: 
            for embed in recent_message.embeds:
                await recreated_channel.send(embed=embed)
        else: 
            await recreated_channel.send(content=recent_message.content)
            
        
        
        await recreated_channel.send("Channel has been nuked.")





        
    @app_commands.command(name="purge",description="Delete a number of messages from the channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def purge(self, inter:discord.Interaction, amount:int):
        await inter.response.defer(ephemeral=True)
        if amount > 100:
            await inter.followup.send("You can only delete 100 messages at a time", ephemeral=True)
            return
        await inter.channel.purge(limit=amount)
        await inter.followup.send(f"Deleted {amount} messages", ephemeral=True)
        
    @app_commands.command(name="userpurge",description="Delete a number of messages from a user in the channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def userpurge(self, inter:discord.Interaction, user:discord.Member, amount:int):
        await inter.response.defer(ephemeral=True)
        if amount > 100:
            await inter.followup.send("You can only delete 100 messages at a time", ephemeral=True)
            return
        await inter.channel.purge(limit=amount, check=lambda m: m.author == user)
        await inter.followup.send(f"Deleted {amount} messages from {user}", ephemeral=True)
        
    @app_commands.command(name="transfer-slot",description="Transfer a slot to another user")
    @app_commands.checks.has_permissions(administrator=True)
    async def transfer_slot(self, inter:discord.Interaction, slot_owner:discord.Member, new_owner:discord.Member):
        await inter.response.defer(ephemeral=True)
        try:
            with open("./database/slot.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []
        for entry in data:
            if entry["owner"] == slot_owner.id:
                entry["owner"] = new_owner.id
                with open("./database/slot.json", "w") as f:
                    json.dump(data, f, indent=2)
                msg = await inter.followup.send(embed=discord.Embed(description=f"Transfering started......."), ephemeral=True)
                ch = inter.guild.get_channel(entry["channel"])
                overwrie = discord.PermissionOverwrite(send_messages=False)
                await inter.followup.edit_message(message_id=msg.id, embed= discord.Embed(description="Transfering the permissions...."))
                await asyncio.sleep(1)
                await ch.set_permissions(slot_owner, overwrite=overwrie)
                await asyncio.sleep(2)
                overwrie2 = discord.PermissionOverwrite(send_messages=True)
                await asyncio.sleep(3)
                await ch.set_permissions(new_owner, overwrite=overwrie2)
                await inter.followup.edit_message(message_id=msg.id,embed=discord.Embed(description="Changing Channel name...."))
                await asyncio.sleep(4)
                
                await ch.edit(name=f"slot-{new_owner.name}")
                embed = discord.Embed(description=f"Slot transferred from {slot_owner.mention} to {new_owner.mention}",color=discord.Color.green())
                await ch.send(embed=embed)
                await inter.followup.edit_message(message_id=msg.id,embed=discord.Embed(description=f"Slot transferred from {slot_owner.mention} to {new_owner.mention}"))
                return
        await inter.followup.send("Slot not found for the user", ephemeral=True)



        
    @app_commands.command(name="recover-slot",description="Recover a slot using recovery code")
    @app_commands.checks.has_permissions(administrator=True)
    async def recover_slot(self, inter:discord.Interaction,slot_giving_to: discord.Member ,recovery_code:str):
        await inter.response.defer(ephemeral=True)
        try:
            with open('./database/slot.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []
        guild = inter.guild_id
        for entry in data:
            if SERVER_ID == guild:
                if entry["recovery_code"] == recovery_code:
                    channel = self.bot.get_channel(entry["channel"])
                    overwrite = discord.PermissionOverwrite(send_messages=False)
                    olduser = await self.bot.fetch_user(entry["owner"])
                    await channel.set_permissions(olduser, overwrite=overwrite)
                    overwrite2 = discord.PermissionOverwrite(send_messages=True)
                    await channel.set_permissions(slot_giving_to, overwrite=overwrite2)
                    new_code = await fu.recovery_code_gen()
                    entry["recovery_code"] = new_code
                    entry["owner"] = inter.user.id
                    with open('./database/slot.json', 'w') as f:
                        json.dump(data, f, indent=2)
                    await channel.edit(name=f"slot-{slot_giving_to.name}")
                    
                    embed = discord.Embed(title="Slot Recovered", color=discord.Color.green())
                    time = await fu.decode_special_code(entry["time"])
                    response = [
                        f"Slot has been recovered by {inter.user.mention}",
                        f"You can start using the slot again",
                        f"Slot will be closed at {time}"
                    ]
                    embed.set_thumbnail(url="https://media.discordapp.net/attachments/1210519710635003915/1211711053583351858/KG6SWxX.png?ex=65ef30db&is=65dcbbdb&hm=cb5d0d67222042093b2ccd51cb2843bdb1a2fc4eae6f05b9e98446d6ef68f707&=&format=webp&quality=lossless&width=640&height=640")
                    embed.description = "\n".join(response)
                    await channel.send(f"{slot_giving_to.mention}",embed=embed)
                    try:
                        role = discord.utils.get(inter.guild.roles, id=ROLE_ID)
                        await slot_giving_to.add_roles(role)
                        await asyncio.sleep(5)
                        await olduser.remove_roles(role)
                    except discord.Forbidden:
                        pass
                    try:
                        await inter.user.send(embed=discord.Embed(description=f"Slot recovered successfully \n You can start using the slot again \n New recovery code has been generated ```{new_code}```"))
                    except discord.Forbidden:
                        await inter.followup.send(embed=discord.Embed(description=f"Slot recovered successfully \n You can start using the slot again \n New recovery code has been generated ```{new_code}```"), ephemeral=True)
                        return
                    await inter.followup.send(embed=discord.Embed(description=f"Slot recovered for {inter.user.mention}"), ephemeral=True)
                    return
        await inter.followup.send("Recovery code not found", ephemeral=True)
        
    @app_commands.command(name="ping-reset",description="Reset ping count if it exceeds the limit")
    @app_commands.checks.has_permissions(administrator=True)
    async def ping_reset(self, inter:discord.Interaction, slot_owner:discord.Member):
        await inter.response.defer(ephemeral=True)
        try:
            with open('./database/slot.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []
        for entry in data:
            if entry["owner"] == slot_owner.id:
                if entry["ping"] > entry["ping_limit"] or entry["everyone_ping"] > entry["everyone_ping_limit"] or entry["everyone_ping"] < entry["everyone_ping_limit"] or entry["ping"] < entry["ping_limit"] or entry["everyone_ping"] == entry["everyone_ping_limit"] or entry["ping"] == entry["ping_limit"]:
                    entry["ping"] = 0
                    entry["everyone_ping"] = 0
                    with open('./database/slot.json', 'w') as f:
                        json.dump(data, f, indent=2)
                    await inter.followup.send(embed=discord.Embed(description=f"Ping count reset for {slot_owner.mention}"), ephemeral=True)
                    return
                await inter.followup.send("Ping count not exceeded the limit", ephemeral=True)
        
            
    @app_commands.command(name="gen-recovery-code",description="Generate a recovery code for a slot")
    @app_commands.checks.has_permissions(administrator=True)
    async def gen_recovery_code(self, inter:discord.Interaction, user:discord.Member):
        await inter.response.defer(ephemeral=True)
        try:
            with open('./database/slot.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []
        for entry in data:
            if entry["owner"] == user.id:
                new_code = await fu.recovery_code_gen()
                entry["recovery_code"] = new_code
                with open('./database/slot.json', 'w') as f:
                    json.dump(data, f, indent=2)
                await inter.followup.send(embed=discord.Embed(description=f"New recovery code has been generated for {user.mention} ```{new_code}```"), ephemeral=True)
                return
        await inter.followup.send("Slot not found for the user", ephemeral=True)

        
    @commands.command(name="myslot")
    async def myslot(self,ctx):
        try:
            with open('./database/slot.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []
        for entry in data:
            if entry["owner"] == ctx.author.id:
                channel = ctx.guild.get_channel(entry["channel"])
                embed = discord.Embed(description=f"Your slot {channel.mention}", color=discord.Color.random())
                await ctx.send(embed=embed)
                return
        await ctx.send("You don't have a slot")
        

    @app_commands.command(name="custom-slot", description="Create a slot")
    @app_commands.checks.has_permissions(administrator=True) 
    @app_commands.choices(slot_category = [
        app_commands.Choice(name="Category 1", value=1),
        app_commands.Choice(name="Category 2", value=2),
        app_commands.Choice(name="Category 3", value=3)
    ])
    async def create_custom_slot(self, inter: discord.Interaction, time: int,slot_category: app_commands.Choice[int],slot_owner: discord.Member, here_ping_limit: int = 3, everyone_ping_limit: int = 0):
        await inter.response.defer(ephemeral=True)
        guild = inter.guild_id
       
        try:
            with open("./database/slot.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []
            
        try:
            role = discord.utils.get(inter.guild.roles, id=ROLE_ID)
            if role is None:
                pass 
            else:
                await slot_owner.add_roles(role)
        except Exception as e:
            print(e)
            pass
        
        exiting_id = [entry for entry in data if entry["owner"] == slot_owner.id and entry["guild_id"] == guild]
        if exiting_id:
            await inter.followup.send(f"Slot already created for {slot_owner.mention}", ephemeral=True)
            return
        try:
            time_revok = datetime.now() + timedelta(days=time)
            
            code = await fu.generate_special_code(time)
            
            recover_code = await fu.recovery_code_gen()
        
            if slot_category.value == 1:
                categoury_id = SlOT_CATEGORY_1
            elif slot_category.value == 2:
                categoury_id = SlOT_CATEGORY_2
            elif slot_category.value == 3:
                categoury_id = SlOT_CATEGORY_3
            
            categoury = discord.utils.get(inter.guild.categories, id=categoury_id)
            overwrites = {
                inter.guild.default_role: discord.PermissionOverwrite(send_messages=False),
                slot_owner: discord.PermissionOverwrite(send_messages=True)
            }
            ch = await categoury.create_text_channel(f"{slot_owner.name}-slot", overwrites=overwrites)
            rule_ch = discord.utils.get(inter.guild.text_channels, id=RULE_CHANNEL_ID)
            embed = discord.Embed(title="Slot Detials", color=discord.Color.blurple())
            stap = f"<t:{int(time_revok.timestamp())}:R>"
            msdd = [
                f"**Purschased At:**\n <t:{int(datetime.now().timestamp())}:R>",
                f"**Duration:**\n{time} Days",
                f"**Expires At:**\n{stap}",
                "**Slot Permissions:**",
                f"```{here_ping_limit}x @here pings\n{everyone_ping_limit}x @everyone pings```",
                f"**Alwasy Accpet MM",
                f"**Must Follow** {rule_ch.mention}",
            ]
            embed.set_image(url=EMBED_IMG_URL)
            embed.description = "\n".join(msdd)
            embed.set_footer(text=f"Slot created by {inter.user.name}")
            embed.timestamp = datetime.now()
            if slot_owner.avatar is None:
                embed.set_thumbnail(url=slot_owner.default_avatar.url)
            else:
                embed.set_thumbnail(url=slot_owner.avatar.url)
            
            embed.set_footer(text="Slot system by Asbron")
            await ch.send(embed=embed,content=slot_owner.mention)
            
            userembed = discord.Embed(title="Slot Information📃", color=discord.Color.green())
            msg = [
                f"Slot Created for you",
                f"Slot Duration: {time} Days",
                f"Slot Ending: {stap}",
                f"if you lost access to the slot use this code to recover the slot ```{recover_code}```",
                f"Here Ping Limit: {here_ping_limit}",
                f"Everyone Ping Limit: {everyone_ping_limit}"
            ]
            userembed.description = "\n".join(msg)
            try:
                await slot_owner.send(embed=userembed)
            except discord.Forbidden:
                pass
            
            entry = {"owner": slot_owner.id, "time": code, "channel": ch.id,"guild_id": guild ,"ping": 0, "ping_limit": here_ping_limit, "everyone_ping": 0 , "everyone_ping_limit": everyone_ping_limit, "recovery_code": recover_code}
            try:
                with open("./database/slot.json", "r") as f:
                    data = json.load(f)
            except FileNotFoundError:
                data = []
            data.append(entry)
            with open("./database/slot.json", "w") as f:
                json.dump(data, f, indent=2)
            await inter.followup.send(embed=discord.Embed(description=f"Slot created for {slot_owner.mention}\n for {time} days \n at {ch.mention}"), ephemeral=True)
        except Exception as e:
            await inter.followup.send(f"Error: {e}", ephemeral=True)
        

        
        
async def setup(bot):
    await bot.add_cog(Slot(bot))
                
            