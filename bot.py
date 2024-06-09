import os
import discord
import random
import requests
import asyncio
import unidecode
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHALLENGE_CHANNEL = 1192740543042682890
ADMIN = 885074776467578900
TRIVIA_API_URL = "https://opentdb.com/api.php?amount=1"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

trivia_active = {} # Jucatorii activi de Trivia

@bot.command(name="iele", help="iti arata niste iele")
async def iele(ctx):
    poze_cu_iele = [
        "https://www.fanatik.ro/wp-content/thumbnails/yfKwS-Gk2jg7ZnW7Z7qj7nXQuXY=/1200x0/smart/filters:contrast(5):format(jpeg):quality(80)/wp-content/uploads/2023/06/iele.jpg",
        "https://i.pinimg.com/originals/3e/dd/d2/3eddd2d60457b71887d96a4bec8b59ac.jpg",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTBkKYBAAlnLVtpdaU7hTBDXbiF_h0GxOWTHw&s",
        "https://miro.medium.com/v2/resize:fit:1200/1*zlHUbLwIRnBkPPDCG_9cUQ.jpeg",
        "https://i.ytimg.com/vi/tItT6uyE4lU/maxresdefault.jpg",
        "https://miro.medium.com/v2/resize:fit:1400/1*hVhsJ8ZhOGQn3idWpoFt2w.jpeg"
    ]
    await ctx.send(random.choice(poze_cu_iele))

@bot.command(name="challenge", help="face un challenge")
async def challenge(ctx, query, ans):
    if ctx.author.id != ADMIN:
        return
    global correct_challenge
    correct_challenge = str(ans)
    channel = bot.get_channel(CHALLENGE_CHANNEL)
    await channel.send(query)

@bot.command(name="answer", help="sa dai raspunsul la challenge")
async def answer(ctx, ans):
    global correct_challenge
    if ans != correct_challenge:
        await ctx.send("WA")
    else:
        await ctx.send("AC")

@bot.command(name="trivia", help="incepi un joc de trivia")
async def trivia(ctx):
    global trivia_active

    if ctx.author.id in trivia_active:
        await ctx.send("Ai deja un joc de trivia activ. Asteapta pana il termini.")
        return

    response = requests.get(TRIVIA_API_URL)
    if response.status_code != 200:
        await ctx.send("Nu am putut prelua intrebarea de trivia momentan.")
        return

    trivia_data = response.json()["results"][0]
    question = trivia_data["question"]
    correct_trivia = trivia_data["correct_answer"]

    await ctx.send(f"{ctx.author.mention}, intrebare: {question}")

    trivia_active[ctx.author.id] = True
    
    try:
        response = await bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=15.0)
    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention}, a expirat timpul! Raspunsul corect era: {correct_trivia}")
    else:
        if response.content.strip().lower() == correct_trivia.lower():
            await ctx.send(f"{ctx.author.mention}, felicitari! Raspunsul tau a fost corect.")
        elif response.content.strip().lower().startswith("!trivia") == False:
            await ctx.send(f"{ctx.author.mention}, raspunsul tau este gresit. Raspunsul corect era: {correct_trivia}")

    if ctx.author.id in trivia_active:
        del trivia_active[ctx.author.id] 

bot.run(TOKEN)
