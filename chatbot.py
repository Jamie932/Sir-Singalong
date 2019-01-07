import glob
import os
import string

from twitchio.ext import commands

class Bot(commands.Bot):
    lyrics = []
    stripped_lyrics = []
    last_messages = {}
    repeat_counts = {}

    def __init__(self):
        super().__init__(irc_token='oauth:kepquk1649d0mli9qyys176e2flk3r', client_id='yfx16nju6icu3bxms1fpwvx1ykom1u',
                         nick='sirsingalot', prefix='', initial_channels=['jamie932'])

    async def event_ready(self):
        print(f'Ready | {self.nick}')
        await self.prepare_songs()

    async def event_message(self, message):
        print("Checking " + message.content)
        await self.check_for_lyrics(message)

    async def prepare_songs(self):
        os.chdir("songs")
        count = 0

        for filename in glob.glob("*.txt"):
            count = count + 1
            with open(filename, 'r') as f:
                lines = f.read().split('\n')
                f.seek(0)
                temp_lines = self.strip_lines(f.read()).split('\n')

                for index, line in enumerate(lines):
                    self.lyrics.append(line)
                    self.stripped_lyrics.append(temp_lines[index])

        print(str(count) + " song(s) parsed.")

    async def check_for_lyrics(self, message):
        message_trimmed = self.strip_lines(message.content)
        author = message.author.name

        if message_trimmed in self.stripped_lyrics:
            ctx = await self.get_context(message)
            occurrences = self.stripped_lyrics.count(message_trimmed)

            self.last_messages[author] = self.last_messages.get(author, "")
            self.repeat_counts[author] = self.repeat_counts.get(author, 1)

            if occurrences > self.repeat_counts[author] and self.last_messages[author] == message_trimmed:
                self.repeat_counts[author] = self.repeat_counts[author] + 1
            else:
                self.repeat_counts[author] = 1

            await ctx.send(self.lyrics[self.stripped_lyrics.index(message_trimmed) + ((self.repeat_counts[author] - 1) * 2) + 1])
            self.last_messages[author] = message_trimmed

    @staticmethod
    def strip_lines(message):
        return message.lower().strip().translate(str.maketrans('', '', string.punctuation))

    async def _get_prefixes(self, message):
        return ""


bot = Bot()
bot.run()
