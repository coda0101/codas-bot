import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import os
import random
from typing import Literal, Optional
import aiohttp

load_dotenv() # load environment variable file
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w') # w: write mode
intents = discord.Intents.all()

class cmd_tree(app_commands.CommandTree):
    def __init__(self, client):
        super().__init__(
            client,
            allowed_contexts=app_commands.AppCommandContext(
                guild=True, dm_channel=True, private_channel=True
            ),
            allowed_installs=app_commands.AppInstallationType(
                guild=True, user=True
            ),
        )

bot = commands.Bot(command_prefix='-', owner_id=638198315158077450, intents=intents, tree_cls=cmd_tree)

@bot.event
async def on_ready():
    print(f"{bot.user.name} is running.")

#censorship
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    banned_words = ["fag"]

    if any(word in message.content.lower() for word in banned_words):
        await message.delete()
        await message.channel.send(f"{message.author.mention} don't use that word!")
        return
    
    await bot.process_commands(message)

@bot.command()
@commands.is_owner()
async def sync(ctx: commands.Context, spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not spec:
        # Syncs all global commands (Can take up to an hour to register everywhere)
        synced = await ctx.bot.tree.sync()
        await ctx.send(f"Synced {len(synced)} commands globally.")
        return

    if spec == "~":
        # Syncs global commands specifically to the CURRENT server (Instant update)
        ctx.bot.tree.copy_global_to(guild=ctx.guild)
        synced = await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"Synced {len(synced)} commands to this local guild.")
        
    elif spec == "*":
        # Syncs everything intended for this specific guild
        synced = await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"Synced {len(synced)} guild-specific commands.")
        
    elif spec == "^":
        # Completely clears and wipes commands from the current guild
        ctx.bot.tree.clear_commands(guild=ctx.guild)
        await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.send("Cleared all commands from this guild.")

# shitposting
@bot.hybrid_command(description="Sends a Minion beedo GIF.")
async def beedo(ctx):
    await ctx.send(f"https://tenor.com/r2FMBr2v7Ve.gif")

@bot.hybrid_command(description="Validates your love for Nick Wilde.")
async def nick(ctx):
    await ctx.send(f"Nick Wilde is a conventionally attractive fox.")

@bot.hybrid_command(description="Sends Tom Lizard.")
async def lizard(ctx):
    await ctx.send(f"https://tenor.com/uEjmKVTvLMg.gif")

woopers = ["https://tenor.com/lp085tBW6Ti.gif", "https://tenor.com/jQiQC27NiKY.gif", "https://tenor.com/rR2q5tdO64z.gif",
           "https://tenor.com/k0OkYjlw9aQ.gif", "https://tenor.com/iFRJ6UGJkTl.gif", "https://tenor.com/bvZ2OfflFJj.gif",
           "https://tenor.com/ecfvTHt8nRI.gif"]

@bot.hybrid_command(description="Sends a random Wooper GIF.")
async def wooper(ctx):
    gif = random.choice(woopers)
    await ctx.send(gif)

ways_to_punch = ["https://raw.githubusercontent.com/coda0101/codas-bot/refs/heads/main/assets/markiplier-punch.gif",
                 "https://raw.githubusercontent.com/coda0101/codas-bot/refs/heads/main/assets/minion-punch.gif",
                 "https://raw.githubusercontent.com/coda0101/codas-bot/refs/heads/main/assets/minion-punch2.gif"]

@bot.hybrid_command(description="Punches a user.")
@app_commands.describe(
    user="The user you want to punch",
)
async def punch (ctx, user: discord.User):
    punch_gif = random.choice(ways_to_punch)
    response = f"{ctx.author.mention} punches {user.mention}!"
    response1 = f"{ctx.author.mention} punches themselves!"
    embed = discord.Embed(title="Someone was punched!", color=discord.Colour.random())
    embed.set_image(url=punch_gif)

    if ctx.author == user:
        await ctx.send(content=response1, embed=embed)
    else:
        await ctx.send(content=response, embed=embed)

@punch.error
async def punch_error(ctx, error):
    if isinstance(error, (commands.MemberNotFound, commands.UserNotFound)):
        await ctx.send("That is not a valid user!")

judgements = ["is cool", "is not cool", "is gay", "is straight (derogatory)", "is mean", "is Satan", "is God",
              "is nice"]

@bot.hybrid_command(description="Judges a person.")
@app_commands.describe(
    person="The person you want to judge",
)
async def judge(ctx, *, person: str):
    judgment = random.choice(judgements)
    await ctx.send(f"{person} {judgment}")

# extra features
def parse_modifier(mod_str):
    """Returns a list of modifier rolls for either NdN or flat number."""
    mod_str = mod_str.strip()
    if 'd' in mod_str:
        rolls, limit = map(int, mod_str.split('d'))
        return [random.randint(1, limit) for _ in range(rolls)]
    else:
        return [int(mod_str)]

# discord utilities
# source: https://github.com/Rapptz/discord.py/blob/v2.7.0/examples/basic_bot.py
@bot.hybrid_command(description="Rolls dice with NdN format")
@app_commands.describe(
    dice="Dice to roll, e.g. 2d6",
    modifier="Optional modifier, e.g. +3 or 1d4"
)
async def roll(ctx, dice: str, *, modifier: str = None):
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await ctx.send('Format has to be in NdN, e.g. 2d6')
        return

    results = [random.randint(1, limit) for _ in range(rolls)]
    result_string = ", ".join(map(str, results))

    if modifier:
        try:
            mod_rolls = parse_modifier(modifier)
            mod_string = ", ".join(map(str, mod_rolls))
            mod_total = sum(mod_rolls)

            modified_results = [r + mod_total for r in results]
            modified_string = ", ".join(map(str, modified_results))

            sign = "+" if mod_total > 0 else ""
            await ctx.send(f"{result_string}\n"
                           f"Modifier: {mod_string} ({sign}{mod_total})\n"
                           f"Unmodified: {result_string}\n"
                           f"**Final: {modified_string}**")
        except Exception:
            await ctx.send('Modifier must be a number or NdN')
    else:
        await ctx.send(f"**{result_string}**")

@bot.tree.command(description="Creates a poll")
@app_commands.describe(
    question="The poll question",
    reactions="Optional: custom emojis separated by spaces. Leave blank for default 👍👎❓"
)
async def createpoll(interaction: discord.Interaction, question: str, reactions: str = None):
    embed = discord.Embed(title=f"📊 {interaction.user.name}'s poll", description=question, color=discord.Colour.random())

    await interaction.response.send_message(embed=embed)
    poll_message = await interaction.original_response()

    emoji_list = reactions.split() if reactions else ["👍", "👎", "❓"]

    failed = []
    for emoji in emoji_list:
        try:
            await poll_message.add_reaction(emoji)
        except discord.HTTPException:
            failed.append(emoji)

    if failed:
        await interaction.followup.send(f"Couldn't add these as reactions: {' '.join(failed)}", ephemeral=True)

@bot.hybrid_command(description="Repeats back your message.")
async def copy(ctx, *, message: str):
    await ctx.send(message)

magic8ball_replies = ["It is certain", "Reply hazy, try again", "Don't count on it", "It is decidedly so",
                      "Ask again later", "My reply is no", "Without a doubt", "Better not tell you now",
                      "My sources say no", "Yes definitely", "Cannot predict now", "Outlook not so good",
                      "You may rely on it", "Concentrate and ask again", "Very doubtful", "As I see it, yes",
                      "Most likely", "Outlook good", "Yes", "Signs point to yes"]
                      
@bot.hybrid_command(description="Ask the Magic 8 Ball a question!")
@app_commands.describe(question="The question you want answered")
async def magic8ball(ctx, *, question: str):
    response = random.choice(magic8ball_replies)
    await ctx.send(f"**Q:** {question}\n**A:** {response}")

# thank you https://dictionaryapi.dev/
@bot.hybrid_command(description="Gets the definition of a word.")
@app_commands.describe(word="The word you want defined")
async def define(ctx, *, word: str):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                await ctx.send(f"No definition found for **{word}**.")
                return
            data = await resp.json()

    entry = data[0]
    output = f"**{entry['word']}**\n"
    def_count = 1

    for meaning in entry.get("meanings", []):
        part_of_speech = meaning.get("partOfSpeech", "unknown")
        for definition in meaning.get("definitions", []):
            line = f"definition {def_count} ({part_of_speech}): {definition['definition']}\n"
            if definition.get("example"):
                line += f"  example: {definition['example']}\n"
            output += line
            def_count += 1

    if len(output) > 1990:
        output = output[:1990] + "..."

    await ctx.send(output)

# coda utils
# credit to aspyn
def owner_check(interaction: discord.Interaction) -> bool:
    return interaction.user.id == interaction.client.owner_id

@bot.tree.command(name="get-username", description="Gets Coda's usernames/IDs for other platforms")
@app_commands.describe(platform="Which platform?", hidden="Hide from others?")
@app_commands.check(owner_check)
@app_commands.choices(platform=[
    app_commands.Choice(name="Honkai Star Rail", value="622852360"),
    app_commands.Choice(name="Nintendo Switch", value="Sw-0302-3963-0622"),
    app_commands.Choice(name="Minion Rush", value="155F3D"),
    app_commands.Choice(name="Pokémon GO", value="449971039763"),
    app_commands.Choice(name="Steam", value="1272623780")
])

async def get_username(interaction: discord.Interaction, platform: app_commands.Choice[str], hidden: bool = True):
    embed = discord.Embed(title=f"{platform.name} user", description=platform.value, color=discord.Colour.random())
    await interaction.response.send_message(embed=embed, ephemeral=hidden)

@get_username.error
async def get_username_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message("You don't get to access this super secret information about Coda", ephemeral=True)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)