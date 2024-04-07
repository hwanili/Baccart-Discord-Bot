import discord
import random
import datetime
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

admin_id = #어드민 아이디
TOKEN = "" #봇 토큰

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.slash_command(name='nuke', description='채널을 재생성합니다.')
async def nuke(ctx):
    if ctx.guild.get_role(admin_id) in ctx.author.roles:
        aposition = ctx.channel.position
        new = await ctx.channel.clone()
        await ctx.channel.delete()
        await new.edit(position=aposition)
        embed = discord.Embed(title='Nuked', description='Channel Nuked.', color=discord.Color.red())
        await new.send(embed=embed)
    else:
        embed = discord.Embed(title="권한 없음", description="관리자만 사용 가능합니다.", color=discord.Color.red())
        await ctx.respond(embed=embed)

@bot.slash_command(name='인증', description='아래 버튼을 눌러 역할을 지급합니다.')
async def btrole(ctx):
    embed = discord.Embed(title="인증하기", description="아래 버튼을 누르면 역할이 지급됩니다", color=discord.Color.green())
    await ctx.respond(embed=embed, view=RoleButton(ctx))

class RoleButton(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx

    @discord.ui.button(label="인증하기", style=discord.ButtonStyle.green, custom_id="verification_button")
    async def charge(self, button: discord.ui.Button, interaction: discord.Interaction):
        member = interaction.guild.get_member(interaction.user.id)
        roles = discord.utils.get(interaction.guild.roles, name="인증✅")
        await member.add_roles(roles)
        await interaction.response.send_message("인증이 완료되었습니다.", ephemeral=True)

user_balances = {}
user_last_reward_date = {}

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
                return "플레이어"
            else:
                return "뱅커"
        elif player_total < banker_total:
            if choice == '뱅커':
                return "뱅커"
            else:
                return "플레이어"
        else:
            return "무승부"

@bot.slash_command(name='바카라')
async def baccarat(ctx, bet_amount: int, choice: str):
    if bet_amount <= 0:
        await ctx.channel.trigger_typing()  
        embed = discord.Embed(title="오류",description="베팅 금액은 0보다 커야 합니다.", color=discord.Color.red())
        await ctx.respond(embed=embed)
        return

    if choice not in ['플레이어', '뱅커', '무승부']:
        await ctx.channel.trigger_typing()  
        embed = discord.Embed(title="오류",description="올바른 선택을 해주세요: '플레이어', '뱅커', '무승부'", color=discord.Color.red())
        await ctx.respond(embed=embed)
        return

    if ctx.author.id not in user_balances:
        user_balances[ctx.author.id] = 0

    if user_balances[ctx.author.id] < bet_amount:
        await ctx.channel.trigger_typing()  
        embed = discord.Embed(title="오류",description="잔액이 부족합니다.", color=discord.Color.red())
        await ctx.respond(embed=embed)
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
    user_last_reward_date[ctx.author.id] = datetime.date.today()

    await ctx.channel.trigger_typing()  
    embed = discord.Embed(title="바카라",description=f"플레이어 카드: {game.player_cards}\n뱅커 카드: {game.banker_cards}\n{result}이(가) 나왔습니다. {'배팅금액의 2배인 '+str(winnings)+'원을(를) 획득하셨습니다.' if winnings > 0 else '아쉽지만 베팅액을 잃었습니다.'}", color=discord.Color.green())
    await ctx.respond(embed=embed)

@bot.slash_command(name='잔액')
async def balance(ctx):
    if ctx.author.id not in user_balances:
        await ctx.channel.trigger_typing()  
        embed = discord.Embed(title="잔액",description="잔액: 0", color=discord.Color.green())
        await ctx.respond(embed=embed)
    else:
        await ctx.channel.trigger_typing()  
        embed = discord.Embed(title="잔액",description=f"잔액: {user_balances[ctx.author.id]}", color=discord.Color.green())
        await ctx.respond(embed=embed)

@bot.slash_command(name='무료돈')
async def free_money(ctx):
    if ctx.author.id not in user_balances:
        user_balances[ctx.author.id] = 0

    if ctx.author.id in user_last_reward_date and user_last_reward_date[ctx.author.id] == datetime.date.today():
        await ctx.channel.trigger_typing()  
        embed = discord.Embed(title="오류",description="오늘 이미 무료 돈을 받았습니다.", color=discord.Color.red())
        await ctx.respond(embed=embed)
        return

    user_balances[ctx.author.id] += 10000
    user_last_reward_date[ctx.author.id] = datetime.date.today()

    await ctx.channel.trigger_typing()  
    embed = discord.Embed(title="무료 돈 지급",description="하루에 한 번 10000원을 받았습니다!", color=discord.Color.green())
    await ctx.respond(embed=embed)

@bot.slash_command(name='출금')
async def withdraw(ctx, target_user: discord.Member, amount: int):
    if ctx.guild.get_role(admin_id) in ctx.author.roles:
        if amount <= 0:
            await ctx.channel.trigger_typing()  
            embed = discord.Embed(title="오류",description="출금 금액은 0보다 커야 합니다.", color=discord.Color.red())
            await ctx.respond(embed=embed)
            return

        if ctx.author.id not in user_balances or user_balances[ctx.author.id] < amount:
            await ctx.channel.trigger_typing()  
            embed = discord.Embed(title="오류",description="잔액이 부족합니다.", color=discord.Color.red())
            await ctx.respond(embed=embed)
            return

        user_balances[ctx.author.id] -= amount
        if target_user.id not in user_balances:
            user_balances[target_user.id] = 0
        user_balances[target_user.id] += amount

        await ctx.channel.trigger_typing()  
        embed = discord.Embed(title="출금 완료",description=f"{ctx.author.mention}님이 {target_user.mention}님에게 {amount} 만큼의 금액을 출금하였습니다.", color=discord.Color.green())
        await ctx.respond(embed=embed)
    else:
        embed = discord.Embed(title="권한 없음", description="관리자만 사용 가능합니다.", color=discord.Color.red())
        await ctx.respond(embed=embed)

@bot.slash_command(name='입금', description='관리자가 특정 유저에게 돈을 지급합니다.')
async def give_money(ctx, target_user: discord.Member, amount: int):
    if ctx.guild.get_role(admin_id) in ctx.author.roles:
        if amount <= 0:
            await ctx.channel.trigger_typing()  
            embed = discord.Embed(title="오류", description="지급 금액은 0보다 커야 합니다.", color=discord.Color.red())
            await ctx.respond(embed=embed)
            return

        if target_user.id not in user_balances:
            user_balances[target_user.id] = 0
        user_balances[target_user.id] += amount

        await ctx.channel.trigger_typing()  
        embed = discord.Embed(title="돈 지급 완료", description=f"{ctx.author.mention}님이 {target_user.mention}님에게 {amount} 만큼의 금액을 지급하였습니다.", color=discord.Color.green())
        await ctx.respond(embed=embed)
    else:
        embed = discord.Embed(title="권한 없음", description="관리자만 사용 가능합니다.", color=discord.Color.red())
        await ctx.respond(embed=embed)

bot.run(TOKEN)
