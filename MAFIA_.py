import discord, asyncio, math, random
from discord.ext import commands

token="???"
game=discord.Game("마피아")
bot=commands.Bot(command_prefix="!", status=discord.Status.online, activity=game, help_command=None)
on_game=False
stage=""
gamers=[]
gamers_names=[]
votes={}
voted=[]
killed=""
healed=""
invesed=False
mafia_chat=0
doc_chat=0
cop_chat=0
people=[]
gamers_same=[]

timerno=0

def clear():
    global stage
    global votes
    global voted
    global killed
    global healed
    global invesed
    global gamers_same
    stage=""
    votes={}
    voted=[]
    killed=""
    healed=""
    invesd=False
    gamers_same=[]

async def start(ctx):
    global on_game
    global timerno

    localtimerno=0

    timerno+=1
    await asyncio.sleep(600)
    if localtimerno==timerno:
        await ctx.channel.send("10분간 활동이 없어 게임이 삭제되었습니다.")
        clear()

async def restart(ctx):
    await start(ctx)
        
@bot.event
async def on_ready():
    print("ready")

@bot.command()
async def 도움(ctx):
    embed=discord.Embed(title="도움말", color = discord.Colour.random(), description="!도움: 이 메세지를 전송함\n\n!참가: 현재 마피아 게임에 참가하거나 새 게임을 시작함.\n\n!마피아: 개최자(게임을 시작한 사람)만 사용 가능. 게임을 시작.\n\n!참가자: 현재 참가자들을 보여줌.\n\n!탈주: ???:이타치가 왜 강한지 아나?\n\n")
    embed.set_thumbnail(url="https://ppss.kr/wp-content/uploads/2018/07/05-6-540x304.jpg")
    embed.add_field(name="특수 명령어", value="!지목: 마피아 채널의 마피아만 사용 가능. 마피아의 시간에 목표를 지목함.\n\n!치료: 의사 채널의 의사만 사용 가능. 지목한 사람을 살림.\n\n!조사: 경찰 채널의 경찰만 사용 가능. 지목한 사람이 마피아인지를 알려줌.", inline=False)
    embed.set_footer(text="10분간 대기상태에서 활동이 없을시 게임이 중지됨.")
    await ctx.channel.send(embed=embed)

@bot.command()
async def 마피아(ctx):
    clear()
    global on_game
    global gamers
    global gamers_names
    global gamers_same
    global spoken
    txt=""
    if len(gamers)==0:
        await ctx.channel.send("아직 참가자가 없습니다.")
        return
    
    if ctx.message.author==gamers[0]:
        if on_game==False:
            if len(gamers)>2:
                for gamer in gamers:
                    if gamers.index(gamer)!=len(gamers)-1:
                        txt+=gamer.mention+"님, "
                    else:
                        on_game=True
                        gamers_same=gamers
                        spoken=False
                        txt+=gamer.mention+"님과의 마피아 게임을 시작합니다.\n"
                        await ctx.channel.send(txt)
                        await game_start(ctx)
            else:
                await ctx.channel.send("참가자의 수가 적어 게임을 시작할 수 없습니다.")
        else:
            await ctx.channel.send("이미 게임이 진행 중입니다.")
    else:
        await ctx.channel.send("개최자만이 게임을 시작할 수 있습니다.")

@bot.command()
async def 참가(ctx):
    global on_game
    global gamers
    global gamers_names

    if on_game==False:
        if not(ctx.message.author in gamers):
            gamers.append(ctx.message.author)
            gamers_names.append(mtn(ctx.message.author))
            if len(gamers)==1:
                await ctx.channel.send((ctx.message.author).mention+"님께서 마피아 게임을 개최하셨습니다.")
                await start(ctx)
            else:
                await ctx.channel.send((ctx.message.author).mention+"님께서 "+gamers[0].mention+"님의 게임에 참가하셨습니다.")
                await restart(ctx)
        else:
            await ctx.channel.send((ctx.message.author).mention+"님께서는 이미 게임에 참가하셨습니다.")
            await restart(ctx)
    else:
        await ctx.channel.send("이미 게임이 시작하였습니다. 게임이 끝난 뒤에 참가해 주세요.")

@bot.command()
async def 탈주(ctx):
    global on_game
    global gamers
    global gamers_names
    if on_game==False and (ctx.message.author in gamers):
        await ctx.channel.send((ctx.message.author).mention+"님께서 게임을 떠났습니다.")
        gamers.remove(ctx.message.author)
        gamers_names.remove(mtn(ctx.message.author))
        await restart(ctx)
    elif on_game==True:
        await ctx.channel.send("게임이 진행 중입니다. 시민으로써의 의무를 다하세요.")
    elif not(ctx.message.author in gamers):
        await ctx.channel.send((ctx.message.author).mention+"님은 게임에 참여하고 있지 않으십니다.")

@bot.command()
async def 투표(ctx):
    global on_game
    global gamers
    global stage
    global voted

    if on_game==True:
        if stage=="day":
            if not(ctx.message.author in voted):
                if ctx.message.mentions[0] in gamers:
                    voted.append(ctx.message.author)
                    votes[ctx.message.mentions[0]]+=1
                else:
                    await ctx.channel.send(ctx.message.mentions[0].mention+"님은 게임에 참가하지 않으셨습니다.")
            else:
                await ctx.channel.send(ctx.message.author.mention+"님께서는 이미 투표하셨습니다.")
        else:
            await ctx.channel.send("투표는 투표시간에!")
    else:
        await ctx.channel.send("게임이 아직 시작하지 않았습니다.")

@bot.command(pass_context=True)
async def 지목(ctx):
    global gamers_names
    global stage
    global killed
    global mafia_chat
    
    called=ctx.message.content.split(" ")
    if on_game==True:
        if len(called)>0:
            called=called[1]
        else:
            await ctx.channel.send("제대로 된 형식으로 지목해 주십시오.")
            return
    else:
        await ctx.channel.send("게임이 아직 시작하지 않았습니다.")
        return
    
    if ctx.channel==mafia_chat:
        if stage=="mafia":
            if killed=="":
                if called in gamers_names:
                    await ctx.channel.send(called+"님을 지목하셨습니다.")
                    killed=called
                else:
                    await ctx.channel.send(called+"님은 게임에 참여하고 있지 않으십니다.")
            else:
                await ctx.channel.send("이미 지목을 마치셨습니다.")
        else:
            await ctx.channel.send("마피아의 시간에만 지목 및 토론을 해 주십시오.")
    else:
        await ctx.channel.send("이곳은 마피아 채널이 아닙니다.")

@bot.command(pass_context=True)
async def 치료(ctx):
    global gamers_names
    global stage
    global healed
    global doc_chat
    
    called=ctx.message.content.split(" ")
    if on_game==True:
        if len(called)>0:
            called=called[1]
        else:
            await ctx.channel.send("제대로 된 형식으로 지목해 주십시오.")
            return
    else:
        await ctx.channel.send("게임이 아직 시작하지 않았습니다.")
        return
       
    if ctx.channel==doc_chat:
        if stage=="doc":
            if healed=="":
                if called in gamers_names:
                    await ctx.channel.send(called+"님을 지목하셨습니다.")
                    healed=called
                else:
                    await ctx.channel.send(called+"님은 게임에 참여하고 있지 않으십니다.")
            else:
                await ctx.channel.send("이미 지목을 마치셨습니다.")
        else:
            await ctx.channel.send("치료 시간에만 지목 및 토론을 해 주십시오.")
    else:
        await ctx.channel.send("이곳은 의사 채널이 아닙니다.")

@bot.command(pass_context=True)
async def 조사(ctx):
    global gamers
    global gamers_names
    global stage
    global invesed
    global doc_chat
    global people
    global on_game
    
    called=ctx.message.content.split(" ")
    if on_game==True:
        if len(called)>0:
            called=called[1]
        else:
            await ctx.channel.send("제대로 된 형식으로 지목해 주십시오.")
            return
    else:
        await ctx.channel.send("게임이 아직 시작하지 않았습니다.")
        return
    
    if ctx.channel==cop_chat:
        if stage=="cop":
            if invesed==False:
                if called in gamers_names:
                    await ctx.channel.send(called+"님을 지목하셨습니다.")
                    await ctx.channel.send(called+"님은 마피아가....")
                    await asyncio.sleep(0.5)
                    if gamers[gamers_names.index(called)] in people[0]:
                        await ctx.channel.send("맞습니다!")
                    else:
                        await ctx.channel.send("아닙니다!")
                    
                else:
                    await ctx.channel.send(called+"님은 게임에 참여하고 있지 않으십니다.")
            else:
                await ctx.channel.send("이미 지목을 마치셨습니다.")
        else:
            await ctx.channel.send("조사 시간에만 지목 및 토론을 해 주십시오.")
    else:
        await ctx.channel.send("이곳은 경찰 채널이 아닙니다.")

@bot.command()
async def 참가자(ctx):
    txt=""
    for gamer in gamers:
        if gamer!=gamers[len(gamers)-1]:
            txt+=mtn(gamer)+"님, "
        else:
            txt+=mtn(gamer)+"님과 함께하고 계십니다."
    if txt=="":
        txt="참가자가 아무도 없습니다."
    await ctx.channel.send(txt)

'''
@bot.command()
async def 재시작(ctx):
    global on_game
    global gamers
    global gamers_names
    clear()
    on_game=False
    gamers=[]
    gamers_names=[]
    await ctx.channel.send("재시작이 완료되었습니다.")
'''
    
def mtn(member):
    return str(member)[0:len(str(member))-5]

def add(lst):
    a=0
    for n in lst:
        a+=n
    return n
    
def getoff(lst, lst2):
    for item in lst:
        lst2.remove(item)
    return lst2

def randomassign():
    global gamers
    lst=[]
    lst=gamers
    
    mafia=0
    doc=0
    cop=0
    norm=0

    num=len(lst)

    mafia=math.floor(num/3)
    doc=math.floor(num/4)
    cop=math.floor(num/5)

    mafia=random.sample(lst, mafia)
    lst=getoff(mafia, lst)
    doc=random.sample(lst, doc)
    lst=getoff(doc, lst)
    cop=random.sample(lst, cop)
    lst=getoff(cop, lst)
    norm=lst

    return [mafia, doc, cop, norm]

async def game_start(ctx):
    global gamers
    global gamers_name
    global on_game
    global stage
    global votes
    global voted
    global killed
    global healed
    global invesed
    global mafia_chat
    global doc_chat
    global cop_chat
    global gamers_same

    clear()
    for channel in ctx.guild.channels:
        if str(channel.type)=="text":
            if channel.name=="mafia":
                mafia_chat=channel
            elif channel.name=="doctor":
                doc_chat=channel
            elif channel.name=="police":
                cop_chat=channel

    gamers_copy=gamers

    for channel in ctx.guild.channels:
        if str(channel.type)=="text":
            if channel.name=="mafia":
                mafia_chat=channel
            elif channel.name=="doctor":
                doc_chat=channel
            elif channel.name=="police":
                cop_chat=channel

    for member in ctx.channel.members:
        await mafia_chat.set_permissions(member, read_messages=False, send_messages=False)
        await doc_chat.set_permissions(member, read_messages=False, send_messages=False)
        await cop_chat.set_permissions(member, read_messages=False, send_messages=False)


    global people
    people=randomassign()
    
    mafia=len(people[0])
    doc=len(people[1])
    cop=len(people[2])
    norm=len(people[3])

    namelst=["마피아", "의사", "경찰"]
    txt=""
    for i in range(0, 3):
        for role in people[i]:
            if len(people[i])>1:
                for person in people[i]:
                    if person!=role:
                        if person!=people[len(people[i])-1]:
                            txt+=mtn(person)+"님, "
                        else:
                            txt+=mtn(person)+"님과 함께 "+namelst[i]+"입니다."
            else:
                txt+="당신은 "+namelst[i]+"입니다!"
            await role.send(txt)

    for person in people[3]:
        await person.send("당신은 시민입니다!")

    for member in people[0]:
        await mafia_chat.set_permissions(member, read_messages=True, send_messages=True)

    for member in people[1]:
        await doc_chat.set_permissions(member, read_messages=True, send_messages=True)

    for member in people[2]:
        await cop_chat.set_permissions(member, read_messages=True, send_messages=True)

    await ctx.channel.send("역할이 배분되었습니다. 지금부터는 회의시간을 제외하고는 아무 말도 하지 말아 주십시오.\n(단, 마피아와 의사는 밤에만 자기들끼리 이야기할 수 있습니다.)")
    await ctx.channel.send("마피아가 "+str(mafia)+"명, 의사가 "+str(doc)+"명, 경찰이 "+str(cop)+"명, 시민이 "+str(norm)+"명 입니다.")

    while on_game:
        
        votes={}
        voted=[]
        killed=""
        healed=""

        if mafia>=doc+cop+norm:
            await ctx.channel.send(":crescent_moon: 마피아의 승리입니다! :crescent_moon:")
            break
        else:
            stage="night"
            await ctx.channel.send(":crescent_moon: 밤이 되었습니다..... 마피아들은 DM해 주십시오 ㅎ(마피아는 한번에 한명밖에 죽일 수 없습니다)")
            stage="mafia"
            await mafia_chat.send("정확히 !지목 ~이름~ 의 형식으로 지목해 주세요.")
            while killed=="":
                await asyncio.sleep(0.3)
            
            if doc>0:
                await ctx.channel.send("마피아가 목표를 지목했습니다... 의사는 살릴 사람을 정해 주세요..(한 사람당 1명씩)")
                stage="doc"
                await doc_chat.send("정확히 !치료 ~이름~ 의 형식으로 지목해 주세요.")
                while healed=="":
                    await asyncio.sleep(0.3)

            if cop>0:
                await ctx.channel.send("경찰은 조사할 사람을 정해 주세요(명당 1인)")
                stage="cop"
                await cop_chat.send("정확히 !조사 ~이름~ 의 형식으로 지목해 주세요.")
                while invesed==False:
                    await asyncio.sleep(0.3)
            
            await ctx.channel.send(":sunny: 아침해가 떴습니다!")

            if doc>0:
                await ctx.channel.send("의사가 환자를...")
                await asyncio.sleep(0.5)
                if killed==healed:
                    await ctx.channel.send("살렸습니다!")
                else:
                    await ctx.channel.send("살리지 못하였습니다..")
                    gamers.remove(gamers[gamers_names.index(killed)])
                    gamers_names.remove(killed)
                    await ctx.channel.send(gamers[gamers_names.index(killed)].mention+"님께서 사망하셨습니다.")
            else:
                print(gamers_names)
                print(gamers)
                await ctx.channel.send(gamers[gamers_names.index(killed)].mention+"님께서 사망하셨습니다.")
                gamers.remove(gamers[gamers_names.index(killed)])
                gamers_names.remove(killed)
            
            if mafia>=doc+cop+norm:
                await ctx.channel.send(":crescent_moon: 마피아의 승리입니다! :crescent_moon:")
                break
            
            for gamer in gamers:
                votes[gamer]=0
            voted=[]
            
            stage="day"
            await ctx.channel.send("회의 겸 투표를 시작하겠습니다!")
                
            while add(votes.values())<len(gamers):
                await asyncio.sleep(0.3)

            done=sorted(votes.values())
            killed=[k for k, v in votes.items() if v == done[0]]

            txt=""
            if done[0]==done[1]:
                for person in killed:
                    txt+=killed[person].mention+"님,"
                txt+="\b"
                await ctx.channel.send("투표가 완료되었습니다!"+txt+"께서 "+str(done[0])+"표로 같은 수의 투표를 받아 아무도 죽지 않았습니다.")

            else:
                await ctx.channel.send("투표가 완료되었습니다! 총 "+str(done[0])+"표를 받으신 "+killed[0].mention+"님, 10초 안에 한마디 남기고 가시죠!")
                await asyncio.sleep(10)
            
                gamers.remove(killed)
                gamers_names.remove(mtn(killed))
                await ctx.channel.send("10초 땡! 자, 가셨습니다.")
            
            if mafia>=doc+cop+norm:
                await ctx.channel.send(":crescent_moon: 마피아의 승리입니다! :crescent_moon:")
                break
            
            elif mafia==0:
                await ctx.channel.send(":sunny: 시민의 승리입니다! :sunny:")
                break
            
            else:
                await ctx.channel.send("죽은 분들은 말씀하시면 안 됩니다!")

    for member in gamers_same:
        if mafia!=0:
            await mafia_chat.set_permissions(member, read_messages=False, send_messages=False)
        if doc!=0:
            await doc_chat.set_permissions(member, read_messages=False, send_messages=False)
        if cop!=0:
            await cop_chat.set_permissions(member, read_messages=False, send_messages=False)

    clear()

        
bot.run(token)
