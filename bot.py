import os
import discord
import random
import requests
import asyncio
import unidecode
from discord.ext import commands
from dotenv import load_dotenv
import html
import sqlite3

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
TRIVIA_API_URL = "https://opentdb.com/api.php?amount=1"
BOT_PREFIX = "!"

con = sqlite3.connect("db")
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)

trivia_active = {} # jucatorii activi de trivia

# este user_id in baza de date?
def is_in_database(user_id):
    cursor = con.cursor()
    # cauta user-ul in baza de date
    res = cursor.execute(f"select * from users where discord_id={user_id};")
    # am gasit ceva?
    if res.fetchall():
        return 1
    # nu am gasit user-ul in baza de date
    return 0

# adauga user_id in baza de date
def add_user_to_database(user_id):
    cursor = con.cursor()
    cursor.execute(f"""
        insert into users (discord_id, banned)
        values ({user_id}, false);
    """)
    con.commit()

# este user_id banat?
def is_banned(user_id):
    cursor = con.cursor()
    res = cursor.execute(f"select * from users where discord_id = {user_id} and banned = true;")
    if res.fetchall():
        return 1
    return 0

@bot.command(name="trivia", help="joaca un meci de trivia")
async def trivia(ctx):
    global trivia_active

    # autorul comenzii este banat: iesire imediata
    if is_banned(ctx.author.id):
        await ctx.send("Esti banat. Daca consideri ca este o greseala, "
            "vorbeste cu un administrator.")
        return

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

@bot.command(name="ban", help="baneaza pe cineva de la acest bot")
async def ban(ctx, user):
    # autorul comenzii este banat: iesire imediata
    if is_banned(ctx.author.id):
        await ctx.send("Esti banat. Daca consideri ca este o greseala, "
            "vorbeste cu un administrator.")
        return
    # taie primele 2 si ultima litera din user, deoarece user-ul primit
    # este de forma <@1249284551570624606>
    user_id = user[2:-1]
    if not is_in_database(user_id):
        add_user_to_database(user_id)
    cursor = con.cursor()
    cursor.execute(f"""
        update users
        set banned = true
        where discord_id={user_id};
    """)
    con.commit()

@bot.command(name="unban", help="pardoneste pe cineva de la acest bot")
async def unban(ctx, user):
    # autorul comenzii este banat: iesire imediata
    if is_banned(ctx.author.id):
        await ctx.send("Esti banat. Daca consideri ca este o greseala, "
            "vorbeste cu un administrator.")
        return
    # taie primele 2 si ultima litera din user, deoarece user-ul primit
    # este de forma <@1249284551570624606>
    user_id = user[2:-1]
    if not is_in_database(user_id):
        add_user_to_database(user_id)
    cursor = con.cursor()
    cursor.execute(f"""
        update users
        set banned = false
        where discord_id={user_id};
    """)
    con.commit()

bot.run(TOKEN)