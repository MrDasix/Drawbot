import pickle
from datetime import datetime

import discord
import random
import os 

TOKEN = os.environ["DISCORD_TOKEN"]
FILE = "EN_draw_words"

emoji_map = {
    "1️⃣":1,
    "2️⃣":2,
    "3️⃣":3,
    "4️⃣":4,
    "5️⃣":5,
    "6️⃣":6,
    "7️⃣":7,
    "8️⃣":8,
    "9️⃣":9,
    "🔟":10
}

def get_random_word():	
    lines = open(FILE).read().splitlines()
    return random.choice(lines)

class MyClient(discord.Client):

    def get_new_word(self):
        self.word = get_random_word()

    def save_info(self):
        self.fullInfo = {
                "word": self.word,
                "ranking": self.ranking,
                "channel_id": self.channel_id,
                "entries":self.entries
            }
        with open('info.pkl', 'wb') as f:
            pickle.dump(self.fullInfo, f)
    
    def load_info(self):
        if os.path.exists('info.pkl'):
            with open('info.pkl', 'rb') as f:
                return pickle.load(f)
        else:
            return {
                "word":get_random_word(),
                "ranking":{},
                "channel_id":None,
                "entries":{}
            }

    def assign_channel(self, channel):
        self.channel_id = channel.id

    async def evaluate(self):
        today = datetime.today().strftime("%Y-%m-%d")

        chn = await self.fetch_channel(self.channel_id)

        for entry_author in self.entries[today]:
            total = 0

            msg = await chn.fetch_message(self.entries[today][entry_author][0])

            for react in msg.reactions:
                if str(react) in emoji_map:
                    total += emoji_map[str(react)] * react.count

            if entry_author in self.ranking:
                self.ranking[entry_author] += total
            else:
                self.ranking[entry_author] = total
            
        self.save_info()

    def get_ranking(self):
        ret = ""
        for k in self.ranking:
            ret += str(k)+": "+str(self.ranking[k])+str(os.linesep) 

        return ret

    async def on_ready(self):
        self.fullInfo = self.load_info()

        print(self.fullInfo)

        self.word = self.fullInfo["word"]
        self.ranking = self.fullInfo["ranking"]
        self.channel_id = self.fullInfo["channel_id"]
        self.entries = self.fullInfo["entries"]

        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):

        text = message.content
        
        #List of commands
        if text.startswith("$"):
            text = text.replace(" ","").lower()
            
            if text == "$word":
                await message.channel.send(self.word)
            elif text == "$newword":
                await self.evaluate()
                self.get_new_word()
                await message.channel.send(self.word)
            elif text == "$assignchannel":
                self.assign_channel(message.channel)
            elif text == "$ranking":
                await message.channel.send(self.get_ranking())

        #Entry
        if message.channel.id == self.channel_id:
            if len(message.attachments) > 0:
                print("Added entry",message.attachments[0].url)
                today = datetime.today().strftime("%Y-%m-%d")

                if today not in self.entries:
                    self.entries[today] = {}

                self.entries[today][message.author.name] = (message.id, message.attachments[0].url)


if __name__ == "__main__":
    client = MyClient()
    client.run(TOKEN)	