import os
import discord
import random
import requests
import asyncio
import unidecode
from discord.ext import commands
from dotenv import load_dotenv
import html

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
TRIVIA_API_URL = "https://opentdb.com/api.php?amount=1"
BOT_PREFIX = "!"
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)

trivia_active = {} # jucatorii activi de trivia

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

@bot.command(name="trivia", help="incepi un joc de trivia")
async def trivia(ctx):
    global trivia_active

    # daca cel care a apelat comanda este deja intr-un joc de trivia
    if ctx.author.id in trivia_active:
        await ctx.send("Ai deja un joc de trivia activ. Asteapta pana il termini.")
        return

    # incercam sa luam o intrebare de trivia de la api
    response = requests.get(TRIVIA_API_URL)
    if response.status_code != 200: # codul returnat este diferit de succes?
        await ctx.send("Nu am putut prelua intrebarea de trivia momentan.")
        return

    # utilizatorul este acum intr-un joc de trivia
    trivia_active[ctx.author.id] = True

    # in trivia_data avem toate informatiile returnate de api
    trivia_data = response.json()["results"][0]

    question = html.unescape(trivia_data["question"]) # intrebarea
    correct_answer = html.unescape(trivia_data["correct_answer"]) # raspunsul corect
    incorrect_answers = [] # raspunsurile incorecte
    for ans in trivia_data["incorrect_answers"]: # pentru fiecare raspuns incorect
        incorrect_answers.append(html.unescape(ans)) # adaugam in lista rapsunsul formatat
    all_answers = incorrect_answers + [correct_answer] # toate raspunsurile
    random.shuffle(all_answers) # reordonam aleator raspunsurile

    # trimitem intrebarea pe discord
    await ctx.send(f"{ctx.author.mention}, intrebare: {question}")

    # vom parcurge toate raspunsurile valabile, pastrand si indicele
    for index, answer in enumerate(all_answers, start=1):
        await ctx.send(f"{index}. {answer}") # trimitem aceasta varianta de raspuns
    
    # verifica daca mesajul curent este raspuns la trivia
    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel \
            and (not message.content.strip().startswith(BOT_PREFIX))
    try:
        # asteptam raspunsul jucatorului
        response = await bot.wait_for("message", check=check, timeout=45.0)
    except asyncio.TimeoutError:
        # jucatorul a ramas fara timp
        await ctx.send(f"{ctx.author.mention}, "
            f"a expirat timpul! Raspunsul corect era: {correct_trivia}")
    else:
        # am primit un raspuns
        # raspuns corect
        if response.content.strip().lower() == correct_answer.lower():
            await ctx.send(f"{ctx.author.mention}, "
                f"felicitari! Raspunsul tau a fost corect.")
        # raspuns gresit
        else:
            await ctx.send(f"{ctx.author.mention}, "
                f"raspunsul tau este gresit. Raspunsul corect era: {correct_answer}")

    # jucatorul a terminat jocul de trivia
    del trivia_active[ctx.author.id]

bot.run(TOKEN)