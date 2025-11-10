import discord
from discord.ext import commands
import ast

def insert_returns(body):
    # Ha az utolsó kifejezés egy expression statement, akkor return statement-té alakítjuk
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])
    # If statement-ek esetén a body és az orelse részbe is return-t illesztünk
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)
    # With blokkok esetén is return-t illesztünk a body-ba
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)

class Eval(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='eval', aliases=['e'])
    async def eval_fn(self, ctx, *, cmd):
        fn_name = "_eval_expr"
        cmd = cmd.strip("` ")
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())
        body = f"async def {fn_name}():\n{cmd}"
        parsed = ast.parse(body)
        body = parsed.body[0].body
        insert_returns(body)
        env = {
            'bot': self.bot,
            'discord': discord,
            'commands': commands,
            'ctx': ctx,
            '__import__': __import__
        }
        exec(compile(parsed, filename="<ast>", mode="exec"), env)
        result = await eval(f"{fn_name}()", env)
        await ctx.send(result)

bot = commands.Bot(command_prefix='c?')

async def setup(bot):
    await bot.add_cog(eval(bot))