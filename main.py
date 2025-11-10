import discord
from discord.ext import commands
import config
from colorama import Fore, Style, Back
from files.help import HelpView
from files.view import SlotView1


bot = commands.Bot(command_prefix="?", intents=discord.Intents.all(), help_command=None)   


@bot.command()
@commands.is_owner()
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send("Synced")


@bot.command()
@commands.is_owner()
async def reload(ctx, extension):
    bot = ctx.bot
    await bot.reload_extension(f"files.{extension}")
    await ctx.send(f"Reloaded {extension}")
    
from colorama import Fore, Style

@bot.event
async def on_ready():
    cog_list = ["slots", "error", 'slotauto', 'ping', 'help']
    view_list = ['SlotView1','HelpView']

    loaded_cogs = []
    failed_cogs = []

  
    bot_name = f"{bot.user.name}"
    developer_name = "𝒙𝑳𝒊𝒕𝒐"
    bot_ver = "v1.0 | next update in work..."
    bot_id = f"{bot.user.id}"
    bot_token = f"{config.TOKEN}"

    print(f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{' '*20} {bot_name} {' '*19}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")

    print(f"\n{Fore.YELLOW}{'-' * 50}")
    print(f"{Fore.YELLOW}Bot successfully started.")
    print(f"{Fore.YELLOW}{'-' * 50}{Style.RESET_ALL}")
    print(f"Logged in as {bot_name}!")
    print(f"BOT ID: {bot_id}!")
    print(f"Developer: {developer_name}")
    print(f"Token: {bot_token}")
    print(f"Version: {bot_ver}")

    print(f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")
    print(f"{Fore.RED}The bot launched, 69 SHADES{Style.RESET_ALL}")


    


bot.run(config.TOKEN)