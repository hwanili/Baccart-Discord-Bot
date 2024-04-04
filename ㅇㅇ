import discord
import random
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
TOKEN = ""
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

user_balances = {}  # 사용자의 잔액을 저장할 딕셔너리

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

class BaccaratGame:
    def __init__(self, bet_amount):
        self.bet_amount = bet_amount
        self.player_cards = []
        self.banker_cards = []

    def deal_cards(self):
        deck = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'] * 4
        deck = list(deck)
        random.shuffle(deck)
        self.player_cards = [deck.pop(), deck.pop()]
        self.banker_cards = [deck.pop(), deck.pop()]

    def calculate_total(self, cards):
        total = 0
        for card in cards:
            if card.isdigit():
                total += int(card)
            elif card in ['J', 'Q', 'K']:
                total += 10
            else:
                total += 1
        return total

    def calculate_result(self, choice):
        player_total = self.calculate_total(self.player_cards)
        banker_total = self.calculate_total(self.banker_cards)
        if player_total > banker_total:
            if choice == '플레이어':
                return "Player wins!"
            else:
                return "Banker wins!"
        elif player_total < banker_total:
            if choice == '뱅커':
                return "Banker wins!"
            else:
                return "Player wins!"
        else:
            return "Tie!"

@bot.slash_command(name='바카라')
async def baccarat(ctx, bet_amount: int, choice: str):
    if bet_amount <= 0:
        await ctx.respond("베팅 금액은 0보다 커야 합니다.")
        return

    if choice not in ['플레이어', '뱅커', '무승부']:
        await ctx.respond("올바른 선택을 해주세요: '플레이어', '뱅커', '무승부'")
        return

    if ctx.author.id not in user_balances:
        user_balances[ctx.author.id] = 0

    if user_balances[ctx.author.id] < bet_amount:
        await ctx.respond("잔액이 부족합니다.")
        return

    game = BaccaratGame(bet_amount)
    game.deal_cards()
    result = game.calculate_result(choice)

    winnings = 0
    if result == choice:
        winnings = bet_amount * 2
        user_balances[ctx.author.id] += winnings
    else:
        user_balances[ctx.author.id] -= bet_amount

    await ctx.respond(f"플레이어 카드: {game.player_cards}\n뱅커 카드: {game.banker_cards}\n{result}이 나왔습니다. {'당첨입니다! 배팅금액의 2배인 '+str(winnings)+'를 획득하셨습니다!' if winnings > 0 else '아쉽지만 베팅금액을 잃었습니다.'}")

@bot.slash_command(name='잔액')
async def balance(ctx):
    if ctx.author.id not in user_balances:
        await ctx.respond("잔액: 0")
    else:
        await ctx.respond(f"잔액: {user_balances[ctx.author.id]}")

@bot.slash_command(name='입금')
async def deposit(ctx, amount: int):
    if amount <= 0:
        await ctx.respond("입금 금액은 0보다 커야 합니다.")
        return

    if ctx.author.id not in user_balances:
        user_balances[ctx.author.id] = 0

    user_balances[ctx.author.id] += amount
    await ctx.respond(f"{amount} 만큼의 금액을 입금하였습니다.")
bot.run(TOKEN)
