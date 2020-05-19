import numpy as np
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

    def save_ranking(self):
        np.save('ranking.npy', self.ranking)
    
    def load_ranking(self):
        if os.path.exists('ranking.npy'):
            return np.load('ranking.npy',allow_pickle='TRUE').item()
        else:
            return {}

    def assignChannel(self, channel):
        self.channel_id = channel.id

    def evaluate():
        for entry_author in self.entries[datetime.today]:
            total = 0
            for react in self.entries[datetime.today][entry_author][0].reactions:
                total += emoji_map[str(react)] * react.count

            self.ranking[entry_author] += total
            
        self.save_ranking()

    async def on_ready(self):
        self.word = get_random_word()
        self.ranking = self.load_ranking()
        self.channel_id = None
        self.entries = {datetime.today:{}}

        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):

        text = message.content
        
        #List of commands
        if text.startswith("$"):
            text = text.replace(" ","").lower()
            
            if text == "$word":
                await message.channel.send(self.word)
            elif text == "$newword":
                self.get_new_word()
                await message.channel.send(self.word)
            elif text == "$assignchannel":
                assignChannel(message.channel)
        
        #Entry
        if message.channel.id == self.channel_id:
            if len(message.attachments) > 0:
                self.entries[datetime.today][message.author.discriminator] = (message, message.attachments.url)


if __name__ == "__main__":
    client = MyClient()
    client.run(TOKEN)	