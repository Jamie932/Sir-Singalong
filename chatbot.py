import glob
import os
import string
import random
import time

from twitchio.ext import commands


class Bot(commands.Bot):
    loaded_songs = []
    lyrics = []
    stripped_lyrics = []
    last_messages = {}
    repeat_counts = {}

    user_roles = {}
    characters = ["Mickey Mouse", "Donald Duck", "Goofy", "Minnie Mouse", "Pluto", "Tinkerbell",
                  "Winnie the Pooh", "Stitch", "Lilo", "Snow White", "Cinderella", "Ariel", "Mulan",
                  "Baymax", "Mike Wazowski"]

    def __init__(self):
        super().__init__(irc_token='oauth:kepquk1649d0mli9qyys176e2flk3r', client_id='yfx16nju6icu3bxms1fpwvx1ykom1u',
                         nick='sirsingalot', prefix='', initial_channels=['jamie932'])

    async def event_ready(self):
        print(self.nick + " is ready for action.")
        await self.prepare_songs()

    async def event_message(self, message):
        if message.content[0] == "!":
            await self.handle_commands(message)
        else:
            await self.check_for_lyrics(message)

    async def prepare_songs(self):
        count = 0

        for filename in glob.iglob("songs/**/*.txt", recursive=True):
            self.loaded_songs.append(os.path.basename(filename).replace(".txt", ""))
            count = count + 1

            with open(filename, 'r') as f:
                lines = (line.rstrip() for line in f)
                lines = list(line.replace("\n", "") for line in lines if line)
                f.seek(0)
                temp_lines = list(self.strip_lines(line).replace("\n", "") for line in lines if line)

                print(temp_lines)

                for index, line in enumerate(lines):
                    self.lyrics.append(line)
                    self.stripped_lyrics.append(temp_lines[index])

                self.lyrics.append("")
                self.stripped_lyrics.append("")

        print(str(count) + " song(s) parsed.")

    async def check_for_lyrics(self, message):
        author = message.author.name

        if self.is_lyric(message.content):
            ctx = await self.get_context(message)
            message_trimmed = self.strip_lines(message.content)
            occurrences = self.stripped_lyrics.count(message_trimmed)

            self.last_messages[author] = self.last_messages.get(author, "")
            self.repeat_counts[author] = self.repeat_counts.get(author, 1)

            if occurrences > self.repeat_counts[author] and self.last_messages[author] == message_trimmed:
                self.repeat_counts[author] = self.repeat_counts[author] + 1
            else:
                self.repeat_counts[author] = 1

            lyric_index = self.stripped_lyrics.index(message_trimmed)
            await ctx.send(self.lyrics[lyric_index + ((self.repeat_counts[author] - 1) * 2) + 1])
            self.last_messages[author] = message_trimmed
            return True
        else:
            return False

    @commands.command(name='whoami')
    async def who_am_i(self, ctx):
        if ctx.author.name not in self.user_roles:
            self.user_roles[ctx.author.name] = random.choice(self.characters)
            await ctx.send(f"Ah {ctx.author.name.title()} - let me see here.")
            time.sleep(4)
            await ctx.send("With a flash of my wand...")
            time.sleep(2)
            await ctx.send("And a bippity, boppity boo...")
            time.sleep(2)
            await ctx.send("You are now " + self.user_roles[ctx.author.name] + "!")
        else:
            await ctx.send(f'Hello again {self.user_roles[ctx.author.name]}!')

    @commands.command(name='whatsongs')
    async def what_songs(self, ctx):
        await ctx.send("The currently available songs to sing with me are: " + ', '.join(self.loaded_songs))

    def is_lyric(self, message):
        return self.strip_lines(message) in self.stripped_lyrics

    @staticmethod
    def strip_lines(message):
        return message.lower().strip().translate(str.maketrans('', '', string.punctuation))

    async def _get_prefixes(self, message):
        if not self.is_lyric(message.content):
            return "!"
        return ""

    async def event_pubsub(self, data):
        pass


bot = Bot()
bot.run()
