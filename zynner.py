import discord
from discord.ext import commands
import random
from pathlib import Path  # <-- needed for reading file

# ============ TOKEN LOADING ============
documents_folder = Path.home() / "Documents"
token_file = documents_folder / "token.txt"

if not token_file.exists():
    print(f"❌ Could not find token file at: {token_file}")
    exit()

with open(token_file, "r") as f:
    TOKEN = f.read().strip()

# ============ WHITELIST ============
WHITELISTED_GUILD_IDS = {
    1399489973337591818,
    1399148195627405312
}

# ============ BOT SETUP ============
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ============ LOG CHANNEL ============
LOG_CHANNEL_ID = 1399495207275335680
WELCOME_CHANNEL_ID = 1399489973337591820

async def send_log(embed):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel:
        await channel.send(embed=embed)
    else:
        print("⚠️ Log channel not found")

# ============ EVENTS ============

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    for guild in bot.guilds:
        if guild.id not in WHITELISTED_GUILD_IDS:
            print(f"🚪 Leaving unauthorized guild: {guild.name} ({guild.id})")
            await guild.leave()

@bot.event
async def on_guild_join(guild):
    if guild.id not in WHITELISTED_GUILD_IDS:
        print(f"🚪 Left guild {guild.name} ({guild.id}) because it's not whitelisted.")
        await guild.leave()

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        await channel.send(f"yooooo you made it!!!! read the rules before u do anything btw {member.mention}")
    else:
        print("⚠️ Welcome channel not found")

# ============ WHITELIST COMMAND CHECK ============

@bot.check
async def globally_block_non_whitelisted(ctx):
    if ctx.guild is None:
        return True  # Allow DMs
    if ctx.guild.id not in WHITELISTED_GUILD_IDS:
        await ctx.send("please maybe try buying the bot before even using it 🙏")
        return False
    return True

# ============ MODERATION ============

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"👢 Kicked {member.mention} | Reason: {reason}")
    embed = discord.Embed(title="User Kicked", color=discord.Color.orange())
    embed.add_field(name="User", value=f"{member} ({member.id})", inline=False)
    embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=False)
    embed.add_field(name="Reason", value=reason or "No reason provided", inline=False)
    await send_log(embed)

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 Banned {member.mention} | Reason: {reason}")
    embed = discord.Embed(title="User Banned", color=discord.Color.red())
    embed.add_field(name="User", value=f"{member} ({member.id})", inline=False)
    embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=False)
    embed.add_field(name="Reason", value=reason or "No reason provided", inline=False)
    await send_log(embed)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Cleared {amount} messages", delete_after=3)
    embed = discord.Embed(title="Messages Cleared", color=discord.Color.blue())
    embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=False)
    embed.add_field(name="Channel", value=ctx.channel.mention, inline=False)
    embed.add_field(name="Amount", value=str(amount), inline=False)
    await send_log(embed)

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    guild = ctx.guild
    muted_role = discord.utils.get(guild.roles, name="Muted")
    if not muted_role:
        muted_role = await guild.create_role(name="Muted")
        for channel in guild.channels:
            await channel.set_permissions(muted_role, speak=False, send_messages=False)
    await member.add_roles(muted_role, reason=reason)
    await ctx.send(f"🔇 Muted {member.mention} | Reason: {reason}")
    embed = discord.Embed(title="User Muted", color=discord.Color.dark_gray())
    embed.add_field(name="User", value=f"{member} ({member.id})", inline=False)
    embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=False)
    embed.add_field(name="Reason", value=reason or "No reason provided", inline=False)
    await send_log(embed)

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if muted_role in member.roles:
        await member.remove_roles(muted_role)
        await ctx.send(f"🔊 Unmuted {member.mention}")
        embed = discord.Embed(title="User Unmuted", color=discord.Color.green())
        embed.add_field(name="User", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=False)
        await send_log(embed)
    else:
        await ctx.send(f"ℹ️ {member.mention} is not muted.")

@bot.command()
@commands.has_permissions(kick_members=True)
async def warn(ctx, member: discord.Member, *, reason=None):
    await ctx.send(f"⚠️ {member.mention} has been warned | Reason: {reason}")
    embed = discord.Embed(title="User Warned", color=discord.Color.gold())
    embed.add_field(name="User", value=f"{member} ({member.id})", inline=False)
    embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=False)
    embed.add_field(name="Reason", value=reason or "No reason provided", inline=False)
    await send_log(embed)

# ============ UTILITY ============

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! {latency}ms")

@bot.command()
async def say(ctx, *, message):
    await ctx.message.delete()
    await ctx.send(message)

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"User Info - {member}", color=discord.Color.blue())
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"))
    embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"))
    embed.set_thumbnail(url=member.avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"Server Info - {guild.name}", color=discord.Color.green())
    embed.add_field(name="Owner", value=guild.owner)
    embed.add_field(name="Members", value=guild.member_count)
    embed.add_field(name="Roles", value=len(guild.roles))
    embed.set_thumbnail(url=guild.icon.url if guild.icon else "")
    await ctx.send(embed=embed)

# ============ FUN ============

@bot.command()
async def coinflip(ctx):
    result = random.choice(["🪙 Heads", "🪙 Tails"])
    await ctx.send(result)

@bot.command(aliases=["8ball"])
async def _8ball(ctx, *, question):
    responses = [
        "Yes.", "No.", "Maybe.", "Definitely.", "Absolutely not.",
        "Ask again later.", "It is certain.", "Very doubtful."
    ]
    await ctx.send(f"🎱 Question: {question}\nAnswer: {random.choice(responses)}")

# ============ COMMANDS LIST ============

@bot.command(name="commands")
async def list_commands(ctx):
    embed = discord.Embed(title="📜 Available Commands", color=discord.Color.gold())
    embed.add_field(name="Moderation", value=(
        "`!kick @user [reason]`\n"
        "`!ban @user [reason]`\n"
        "`!clear [amount]`\n"
        "`!mute @user [reason]`\n"
        "`!unmute @user`\n"
        "`!warn @user [reason]`"
    ), inline=False)
    embed.add_field(name="Utility", value=(
        "`!ping`\n"
        "`!say [message]`\n"
        "`!userinfo [@user]`\n"
        "`!serverinfo`"
    ), inline=False)
    embed.add_field(name="Fun", value=(
        "`!coinflip`\n"
        "`!8ball [question]`\n"
        "`!commands`"
    ), inline=False)
    embed.set_footer(text="Prefix: !")
    await ctx.send(embed=embed)

# ============ ERROR HANDLING ============

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 You don't have permission to do that.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ Missing arguments.")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        await ctx.send("❌ An unexpected error occurred.")
        raise error

# ============ RUN ============

bot.run(TOKEN)
