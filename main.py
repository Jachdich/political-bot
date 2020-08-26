import discord, random, asyncio, json

with open("data.json", "r") as f:
    data = {}#json.loads(f.read())

with open("token.txt", "r") as f:
    TOKEN = f.read().split("\n")[0]
client = discord.Client()
@client.event
async def on_ready():
    print("Logged in as", client.user.name, client.user.id)

async def timer():
    pass

async def save_data():
    with open("data.json", "w") as f:
        f.write(json.dumps(data))

async def process_party_command(msg):
    bits = msg.content.split(" ")
    if bits[1] == "create":
        if len(bits) < 3: await msg.channel.send("Error: expected name after /party create"); return
        role = await msg.author.guild.create_role(name=" ".join(bits[2:]))
        await role.edit(hoist=True, mentionable=True, colour=discord.Colour.from_rgb(0xFF, 0xFF, 0x00))
        await msg.author.edit(roles=msg.author.roles + [role,])

        cat = await msg.author.guild.create_category(name=" ".join(bits[2:]))

        overwrites = {
            msg.author.guild.default_role: discord.PermissionOverwrite(read_messages=False)
        }
        await msg.author.guild.create_text_channel("party-private", category=cat, overwrites=overwrites)
        await msg.author.guild.create_text_channel("party-public", category=cat)

        await msg.author.guild.create_voice_channel("party-private", category=cat) #TODO make private
        await msg.author.guild.create_voice_channel("party-public", category=cat)

        data["parties"].append({"members": [], "role-id": role.id, "name": " ".join(bits[2:]), "leader": msg.author.id, "category-id": cat.id})

    if bits[1] == "delete":
        if len(bits) < 3: await msg.channel.send("Error: expected name after /party delete"); return
        if not party["leader"] == msg.author.id: await msg.channel.send("Error: you must be party leader/creator to")
        name = " ".join(bits[2:])

        for cat in msg.author.guild.categories:
            if cat.id == "": pass
            for chan in cat.channels:
                await chan.delete()

        
                data["parties"].remove(party)
                break

async def process_command(msg):
    txt = msg.content
    if txt.startswith("/party"):
        await process_party_command(msg)

    await save_data()
    
    
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("/"):
        await process_command(message)
        

client.loop.create_task(timer())
client.run(TOKEN)
