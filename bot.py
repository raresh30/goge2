import os
import discord
import random
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHALLENGE_CHANNEL = 1192740543042682890
ADMIN = 885074776467578900

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# cateva poze cu iele
poze_cu_iele = [
    "https://www.fanatik.ro/wp-content/thumbnails/yfKwS-Gk2jg7ZnW7Z7qj7nXQuXY=/1200x0/smart/filters:contrast(5):format(jpeg):quality(80)/wp-content/uploads/2023/06/iele.jpg",
    "https://i.pinimg.com/originals/3e/dd/d2/3eddd2d60457b71887d96a4bec8b59ac.jpg",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTBkKYBAAlnLVtpdaU7hTBDXbiF_h0GxOWTHw&s",
    "https://miro.medium.com/v2/resize:fit:1200/1*zlHUbLwIRnBkPPDCG_9cUQ.jpeg",
    "https://i.ytimg.com/vi/tItT6uyE4lU/maxresdefault.jpg",
    "https://miro.medium.com/v2/resize:fit:1400/1*hVhsJ8ZhOGQn3idWpoFt2w.jpeg"
]

challenge_answer = ""

@bot.command(name="iele", help="iti arata niste iele")
async def iele(ctx):
    await ctx.send(random.choice(poze_cu_iele))

@bot.command(name="challenge", help="face un challenge")
async def challenge(ctx, query, ans):
    if ctx.author.id != ADMIN:
        return
    global challenge_answer
    challenge_answer = ans
    channel = bot.get_channel(CHALLENGE_CHANNEL)
    await channel.send(query)

@bot.command(name="answer", help="sa dai raspunsul la challenge")
async def answer(ctx, ans):
    global challenge_answer
    if ans != challenge_answer:
        await ctx.send("WA")
    else:
        await ctx.send("AC")

bot.run(TOKEN)
