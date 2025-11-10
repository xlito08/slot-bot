import discord
from discord import app_commands
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        
    @commands.command(name="help")
    async def help_ctx(self,ctx):
        embed = discord.Embed(title="Help", color=discord.Color.random())
        response = [
            f"Welcome to the help command",
            f"Use the dropdown to select a category",
            f"Please note that some commands are only available to certain roles",
            f"Developed by [Asbron] and [x.Lito]",
            f"Thanks for using the bot!"
        ]
        embed.description = "\n".join(response)
        view = HelpView()
        await ctx.send(embed=embed, view=view)
        
    @app_commands.command(name="help", description="Help command")
    async def help_app(self,interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(title="Help", color=discord.Color.random())
        response = [
            f"Welcome to the  help command",
            f"Use the dropdown to select a category",
            f"Please note that some commands are only available to certain roles",
            f"Developed by [Asbron] and [x.Lito]",
            f"Thanks for using the bot!"
        ]
        embed.description = "\n".join(response)
        view = HelpView()
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
    
        
    
        
    
    
    
    

    
class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(HelpDropDown())
    
    
class HelpDropDown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Slot Owner Commands", description="Slot commands", value="slot"),
            discord.SelectOption(label="Admin Commands", description="Admin commands", value="admin"),
        ]
        super().__init__(placeholder="Select a category", options=options,custom_id="help_dropdown")
        
    async def callback(self,interaction: discord.Interaction):
        value = self.values[0]
        if value == "slot":
            await interaction.response.defer(ephemeral=True)
            embed = discord.Embed(title="Slot Owner Commands", description="Commands for slot owners", color=discord.Color.random())
            embed.add_field(name="?myslot", value="Shows your slot", inline=False)
            embed.add_field(name="?nuke", value="can be used for Cleaning the channel", inline=False)
            await interaction.followup.send(embed=embed, ephemeral=True)
        if value == "admin":
            await interaction.response.defer(ephemeral=True)
            embed = discord.Embed(title="Admin Commands", description="Commands for Admins", color=discord.Color.random())
            embed.add_field(name="/Create Slot", value="Create a slot", inline=False)
            embed.add_field(name="/Delete Slot", value="Delete a slot", inline=False)
            embed.add_field(name="/revoke", value="Revoke a slot", inline=False)
            embed.add_field(name="/hold", value="Hold a slot", inline=False)
            embed.add_field(name="/unhold", value="Unhold a slot", inline=False)
            embed.add_field(name="/ping-reset", value="Ping reset the slot", inline=False)
            embed.add_field(name="This are important comamnds", value="", inline=False)
            await interaction.followup.send(embed=embed, ephemeral=True)
        
            
    
async def setup(bot):
    await bot.add_cog(Help(bot))