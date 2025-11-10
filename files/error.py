import discord 
from discord.ext import commands
from discord import app_commands


class ErrorCog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot 
        bot.tree.on_error = self.on_app_commands_error

    async def on_app_commands_error(self, interaction:discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("You do not have permission",ephemeral=True)
        elif isinstance(error, discord.Forbidden):
            await interaction.response.send_message("Failure occurred",ephemeral=True)

    @commands.Cog.listener()
    async def on_command_error(self,ctx:commands.Context, error:commands.CommandError):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Missing required argument - `{ctx.prefix}{ctx.command.qualified_name} {ctx.command.signature}`",delete_after=5)
        elif isinstance(error, commands.CommandNotFound):
            return await ctx.send("Command not found type `$help`",delete_after=5)
        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send("`You do not have permission to use this cmd`",delete_after=5)
        elif isinstance(error, commands.CommandOnCooldown):
            retry_after_seconds = int(error.retry_after)
            return await ctx.send(f"You are on cooldown wait for `{retry_after_seconds}` seconds", delete_after=5)
        elif isinstance(error, commands.HybridCommandError):
            pass
        elif isinstance(error, discord.NotFound):
            pass
        elif isinstance(error, discord.HTTPException):
            pass
        elif isinstance(error, commands.CheckFailure) and ctx.author.id == ctx.bot.owner_id:
            return await ctx.send("You are the bot owner", delete_after=5)

        else:
            print(f'{error}')

async def setup(bot:commands.bot):
    await bot.add_cog(ErrorCog(bot))