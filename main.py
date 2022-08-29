from multiprocessing.sharedctypes import Value
import nextcord
intents = nextcord.Intents.default()
intents.message_content = True
from nextcord.ext import commands
bot = commands.Bot(command_prefix="$", intents=intents)

import yfinance as yf
from tradingview_ta import TA_Handler, Interval, Exchange
import tradingview_ta

#get prev data
import json
import os

if(not os.path.exists('data.json')):
    with open("data.json","a+") as wfile:
        wfile.write("{")
        wfile.write("}")
f = open('data.json')
data = json.load(f)

print(data)
def savestate():
    for i in data:
        data[i]["money"] = round(data[i]["money"],2)
    with open("data.json", "w") as wfile:
        json.dump(data, wfile, indent=4)

savestate()

def get_info(stockname):
    handler = TA_Handler(
        symbol=stockname,
        exchange="nasdaq",
        screener="america",
        interval="1m"
    )
    analysis = handler.get_analysis()
    return analysis



def exists(id):
    if(str(id) in data):
        return True
    else:
        return False

#Placeholder commands - to make sure bot works.
@bot.command()
async def echo(ctx, arg="ㅤ"):
    await ctx.send(arg)

@bot.command()
async def foo(ctx, arg=1):
    await ctx.send("bar")

@bot.command()
async def getId(ctx, arg=""):
    await ctx.send("<@"+str(ctx.author.id)+">")

#init everything
@bot.command()
async def init(ctx, arg="100000"):
    try:
        if(int(arg)<=0):
            await ctx.send("Starting money must be at least $1")
        else:
            arg = int(arg)
            d2 = {"money": arg, "stocks": {}}
            data[str(ctx.author.id)] = d2
            savestate()
            await ctx.send("Profile created with ${}".format(arg))

    except ValueError:
        await ctx.send("Send a valid integer for starting money")

@bot.command()

async def delete(ctx, arg=""):
    del data[str(ctx.author.id)]
    await ctx.send("Deleted profile")

@bot.command()
async def money(ctx, arg=""):
    if(arg==""):
        arg = str(ctx.author.id)
    try:
        arg = str(arg)
        
        arg = arg.replace("<","")

        arg = arg.replace("@","")
        arg = arg.replace(">","")

        if(arg in data):
            await ctx.send("${}".format(data[str(arg)]["money"]))
        else:
            await ctx.send("User profile not created")
    except ValueError:
        await ctx.send("Type in a proper ID or @ a person")
#get price of a stock
@bot.command()
async def price(ctx, arg=""):
    if(arg==""):
       await ctx.send("Send a stock name")
    else:
        stock_info = yf.Ticker(arg).info
        market_price = stock_info['regularMarketPrice']
        await ctx.send('{} Price: {}'.format(arg, round(market_price,2)))


@bot.command()
async def rec(ctx,stock):
    stock1 = get_info(stock).summary
    await ctx.send("REC: "+stock1['RECOMMENDATION']+"\n\nBUY: "+str(stock1['BUY'])+"\nNEUTRAL: "+str(stock1['NEUTRAL'])+"\nSELL: "+str(stock1['SELL']))

@bot.command()
async def buy(ctx, arg0="", arg1=""):
    if(not exists(ctx.author.id)):
        await ctx.send("User profile not created")
    else:
        try:
            arg = arg0+" "+arg1
            print(arg)
            arg = arg.split(" ")
            arg[1] = int(arg[1])
            if(arg[1] < 1):
                await ctx.send("Number of stocks must be greater than or equal to 1")
            else:
                await ctx.send("Trying to place order...")
                stock_info = yf.Ticker(arg0).info
                market_price = stock_info['regularMarketPrice']
                print(1)
                if(round(data[str(ctx.author.id)]["money"]-market_price*arg[1],2)>=0):

                    i =0
                    while True:
                        if(not str(i) in data[str(ctx.author.id)]["stocks"]):
                            break
                        i+=1
                    print(2)
                    data[str(ctx.author.id)]["money"] -= round(market_price*arg[1],2)
                    data[str(ctx.author.id)]["stocks"][str(i)] = {"stock":arg[0], "amount":arg[1], "price":market_price}
                    await ctx.send("Bought {} shares of {} at ${} per share. Total = ${}".format(arg[1],arg[0],market_price,round(market_price*arg[1],2)))
                    savestate()
                else:

                    await ctx.send("Not enough money")
        except ValueError:
            await ctx.send("Send an integer of number of stocks after the stock symbol.")
        except IndexError:
            await ctx.send("Send 2 arguments: stock symbol and number of shares")

@bot.command()
async def short(ctx, arg0="", arg1=""):
    if(not exists(ctx.author.id)):
        await ctx.send("User profile not created")
    else:
        try:
            arg = arg0+" "+arg1
            print(arg)
            arg = arg.split(" ")
            arg[1] = int(arg[1])
            if(arg[1] < 1):
                await ctx.send("Number of stocks must be greater than or equal to 1")
            else:
                await ctx.send("Trying to place order...")
                stock_info = yf.Ticker(arg0).info
                market_price = stock_info['regularMarketPrice']
                print(1)
                if(round(data[str(ctx.author.id)]["money"]-market_price*arg[1],2)>=0):

                    i =0
                    while True:
                        if(not str(i) in data[str(ctx.author.id)]["stocks"]):
                            break
                        i+=1
                    print(2)
                    data[str(ctx.author.id)]["money"] -= round(market_price*arg[1],2)
                    data[str(ctx.author.id)]["stocks"][str(i)] = {"stock":arg[0], "amount":0-arg[1], "price":market_price}
                    await ctx.send("Shorted {} shares of {} at ${} per share. Total = ${}".format(arg[1],arg[0],market_price,round(market_price*arg[1],2)))
                    savestate()
                else:

                    await ctx.send("Not enough money")
        except ValueError:
            await ctx.send("Send an integer of number of stocks after the stock symbol.")
        except IndexError:
            await ctx.send("Send 2 arguments: stock symbol and number of shares")

@bot.command()
async def profile(ctx, arg=""):
    if(not exists(ctx.author.id)):
        await ctx.send("User profile not created")
    else:

        if(arg==""):
            arg = str(ctx.author.id)
        du = data[arg]
        stocklist = ""
        print(du)
        for i in du["stocks"]:
            i = str(i)
            stocklist+="Trade Id: {}\n".format(i)
            stocklist+="Stock Name: {}\n".format(du["stocks"][i]["stock"])
            stocklist+="Shares: {}\n\n".format(du["stocks"][i]["amount"])

        await ctx.send(
            "Profile of <@{}>\n\n".format(ctx.author.id)+
            "Balance: {}\n\n".format(du["money"])+
            stocklist

        )
        savestate()

@bot.command()
async def close(ctx, arg=""):
    if(not exists(ctx.author.id)):
        await ctx.send("User profile not created")
    else:
            
        if(arg==""):
            await ctx.send("Send the trade ID to close trade")
        try:
            await ctx.send("Trying to close position...")
            stock_info = yf.Ticker(data[str(ctx.author.id)]["stocks"][str(arg)]["stock"]).info
            market_price = stock_info['regularMarketPrice']
            diff = market_price-data[str(ctx.author.id)]["stocks"][str(arg)]["price"]
            diff *= market_price-data[str(ctx.author.id)]["stocks"][str(arg)]["amount"]
            data[str(ctx.author.id)]["money"] += round(diff,2)
            del data[str(ctx.author.id)]["stocks"][str(arg)]
            await ctx.send("Sold Trade #{} for {} per share, with a gain of {}".format(arg,market_price,diff))
            savestate()
        except (ValueError) as e:
            await ctx.send("Send the trade ID to close trade")




key = ""
with open("key.txt") as keyfile:
    for line in keyfile:
        key = line
print("Live!")
bot.run(key)

