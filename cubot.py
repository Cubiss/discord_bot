import asyncio
import datetime
import os
import re
import sqlite3
import random
import sys

import discord

from c__lib.c__input import yes_no_input
from c__lib.c__string import seconds_to_czech_string
from c__lib.c__string import money_string

# todo: Clean up `db` mess.
# todo: Use async wrapper for sqlite3.
# todo: Document everything.
# todo: Forget about this project.
# todo: Server unique currency amount?

epoch_time = datetime.datetime.utcfromtimestamp(0)


class Printer:
    def print(self, *args, **kwargs):
        print(*args, **kwargs)
        sys.stdout.flush()


class Reactor:
    class Reaction:
        def __init__(self, user_id=0, user_name='', emote='', chance=0):
            self.chance = chance
            self.emote = emote
            self.user_name = user_name
            self.user_id = user_id

    def __init__(self):
        self.reaction_list = []

    def load(self, db):
        c = db.cursor()
        c.execute('SELECT ID, USER_ID, USER_NAME, EMOTE, CHANCE from Reactor')

        for row in c.fetchall():
            self.reaction_list.append(
                Reactor.Reaction(
                    user_id=int(row[1]),
                    user_name=str(row[2]),
                    emote=str(row[3])
                )
            )

    pass


class DbUser:
    id: int = 0
    Name: str = ''
    ServerId: int = 0
    AvailableCurrency: int = 0
    CurrentPrize: int = 0
    LastRewardGivenDateTime: datetime.datetime = epoch_time
    LastRewardGainedDateTime: datetime.datetime = epoch_time
    LastCurrencyGainedDateTime: datetime.datetime = epoch_time

    def __init__(self, db: sqlite3.Connection, user_id=None, row=None):
        self.loaded = False
        self.db = db
        if hasattr(user_id, '__iter__'):
            row = user_id
            user_id = None
        if row is not None:
            self.fill_data(row)
        elif user_id is not None:
            self.load(user_id)

    def load(self, user_id: int):
        sql = 'SELECT ' \
              ' ID,' \
              ' Name,' \
              ' ServerId,' \
              ' AvailableCurrency, ' \
              ' CurrentPrize, ' \
              ' LastRewardGivenDateTime, ' \
              ' LastRewardGainedDateTime, ' \
              ' LastCurrencyGainedDateTime ' \
              'FROM ' \
              ' Users ' \
              'WHERE ' \
              ' ID = ?'
        c = self.db.cursor()
        c.execute(sql, [user_id])
        row = c.fetchone()
        if row is not None:
            self.fill_data(row)
            return self
        else:
            self.fill_data(insert_member(self.db, user_id=user_id))

    def fill_data(self, row, other=None):
        if other is not None:
            self.id = other.id
            self.Name = other.Name
            self.AvailableCurrency = other.AvailableCurrency
            self.CurrentPrize = other.CurrentPrize
            self.LastRewardGivenDateTime = other.LastRewardGivenDateTime
            self.LastRewardGainedDateTime = other.LastRewardGainedDateTime
            self.LastCurrencyGainedDateTime = other.LastCurrencyGainedDateTime
        else:
            self.id = row[0]
            self.Name = row[1]
            self.ServerId = row[2]
            self.AvailableCurrency = row[3]
            self.CurrentPrize = row[4]
            self.LastRewardGivenDateTime = db_to_date(row[5])
            self.LastRewardGainedDateTime = db_to_date(row[6])
            self.LastCurrencyGainedDateTime = db_to_date(row[7])

        self.loaded = True

    def update(self):
        self.db.cursor().execute(
            'UPDATE Users set '
            ' Name = ?, '
            ' AvailableCurrency = ?, '
            ' CurrentPrize = ?, '
            ' LastRewardGivenDateTime = ?, '
            ' LastRewardGainedDateTime = ?, '
            ' LastCurrencyGainedDateTime = ?'
            'WHERE ID = ?',
            [self.Name,
             self.AvailableCurrency,
             self.CurrentPrize,
             date_to_db(self.LastRewardGivenDateTime),
             date_to_db(self.LastRewardGainedDateTime),
             date_to_db(self.LastCurrencyGainedDateTime),
             self.id]
        )
        self.db.commit()

    def insert(self):
        self.db.cursor().execute(
            'INSERT INTO Users('
            ' ID,'
            ' Name,'
            ' AvailableCurrency, '
            ' CurrentPrize, '
            ' LastRewardGivenDateTime, '
            ' LastRewardGainedDateTime, '
            ' LastCurrencyGainedDateTime)'
            'VALUES( ?, ?, ?, ?, ?, ?, ?)',
            [self.id,
             self.Name,
             self.AvailableCurrency,
             self.CurrentPrize,
             date_to_db(self.LastRewardGivenDateTime),
             date_to_db(self.LastRewardGainedDateTime),
             date_to_db(self.LastCurrencyGainedDateTime),
             ]
        )
        self.db.commit()

    def __repr__(self):
        if self.Name != '':
            return f'DbUser[{self.Name}]'
        return f'DbUser[{self.id}]'


class Command:
    def __init__(
            self,
            names: list,
            regexp: str,
            command: callable,
            usage=None,
            description='',
            cmd_char='!'):
        """
        Creates a command.
        :param names: Aliases of the command. First name is
        :param regexp: regex representation of messages that can be processed with this command
        :param command: coroutine(message: discord.Message, db: sqlite3.Connection, **kwargs) -> bool:
                        message is message object that command will react to,
                        db is connection to a database
                        kwargs are arguments parsed from regexp groups
        :param usage: String showing how the command should be called.
        :param description: String saying what command should do.
        :param cmd_char: String every command will start with.
        """
        self.db = None
        self.cmd_char = cmd_char
        self.names = names
        self.command = command
        self.re_list = [re.compile(regexp.replace('__name__', cmd_char + name)) for name in names]
        self.usage = usage or f'Command is in wrong format: {self.re_list[0].pattern}'
        self.description = description

    def match(self, message: discord.Message):
        for name in self.names:
            if message.content.lower().startswith(self.cmd_char + name):
                if len(message.content.lower()) > len(self.cmd_char + name):
                    if not message.content.lower()[len(self.cmd_char + name)].isspace():
                        continue
                return True
        else:
            return False

    def run(self, message: discord.Message, client: discord.Client):
        for regex in self.re_list:
            match = regex.match(message.content)
            if match is not None:
                break
        else:
            return message.channel.send(self.format_string(message=message, string=self.usage))

        return self.command(message, self.db, client, **match.groupdict())

    def format_string(self, string: str, message: discord.Message):
        string = string.replace('__name__', self.names[0])
        string = string.replace('__author__', f'<@{message.author.id}>')
        return string


class Cubot(discord.Client):
    commands = list()

    CURRENCY_GAIN_INTERVAL = datetime.timedelta(days=1)
    CURRENCY_GAIN_INCREMENT = 10000

    def __init__(self,
                 database=None,
                 log_commands=False,
                 currency_gain_interval=datetime.timedelta(days=1),
                 currency_gain_increment=10000,
                 *args, **kwargs):
        """
        Inits discord.Client and Cubot
        :param database: Either path to file or
        :param log_commands:
        :param currency_gain_interval:
        :param currency_gain_increment:
        :param args:
        :param kwargs:
        """
        if database is sqlite3.Connection:
            self.database = database
        elif database is str or database is None:
            if database is None:
                database = './cubot.db'
            if os.path.isfile(database):
                self.database = sqlite3.connect(database)
            elif yes_no_input('Database file not found. Should I create and initialize a new one? [y/n]'):
                self.database = sqlite3.connect(database)
                self.init_database(self.database)
            else:
                raise Exception('Database file not found.')

        self.log_commands = log_commands

        self.CURRENCY_GAIN_INCREMENT = currency_gain_increment
        self.CURRENCY_GAIN_INTERVAL = currency_gain_interval

        super(Cubot, self).__init__(*args, **kwargs)

    def addcom(self, command):
        command.db = self.database
        self.commands.append(command)

    async def on_ready(self):
        print(datetime.datetime.now())
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

        for g in self.guilds:
            self.insert_guild_members(g)

        await self.update_all_names()

        await self.update_currencies()

        await self.loop_calls()

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        if message.content.startswith('!help'):
            return await self.help(message)

        # todo: standardize
        if message.author.nick == "blossom":
            if random.randint(0, 100) < 10:
                await message.add_reaction(emoji="blossom:652132199751221269")

        elif message.author.id == 192023454864637952:
            if random.randint(0, 100) < 5:
                await message.add_reaction(emoji="snek:652139158097231872")

        for command in self.commands:
            if command.match(message):
                try:
                    await command.run(message, self)
                    if self.log_commands:
                        print(f'[{datetime.datetime.now()}][{message.guild.name}]{message.author}: {message.content}')
                except Exception:
                    print(message.author)
                    print(message.content)
                    raise

    async def on_member_join(self, member: discord.Member):
        insert_member(self.database, member)
        pass

    async def loop_calls(self):
        await self.update_currencies()
        await asyncio.sleep(60 * 60)

    async def help(self, message: discord.Message):
        help_str = '```'
        help_str += 'Available commands:\n'

        max_command_len = max([len(c.names[0]) for c in self.commands])

        for command in self.commands:
            help_str += f'{command.names[0]:{max_command_len}}: {command.description}\n'

        help_str += '```'

        print(help_str)
        await message.channel.send(help_str)

    def init_database(self, db: sqlite3.Connection = None):
        if db is None:
            db = self.database
        tables_sql = [
            'CREATE TABLE "Transactions" ('
            '	"ID"	INTEGER PRIMARY KEY AUTOINCREMENT,'
            '	"User"	INTEGER,'
            '	"Target"	INTEGER,'
            '	"DateTime"	TEXT,'
            '	"Amount"	INTEGER,'
            '	"Reason"	TEXT'
            ')',
            'CREATE TABLE "Users" ('
            '	"ID"	INTEGER NOT NULL UNIQUE,'
            '	"Name"	TEXT DEFAULT \'-\','
            '	"AvailableCurrency"	INTEGER DEFAULT 0,'
            '	"CurrentPrize"	INTEGER DEFAULT 0,'
            '	"LastRewardGivenDateTime"	TEXT DEFAULT \'1970-01-01 00:00:00.000\','
            '	"LastRewardGainedDateTime"	TEXT DEFAULT \'1970-01-01 00:00:00.000\','
            '	"LastCurrencyGainedDateTime"	TEXT DEFAULT \'1970-01-01 00:00:00.000\','
            '	PRIMARY KEY("ID")'
            ')',
            'CREATE TABLE "CommandLog" ('
            '	"ID"	INTEGER PRIMARY KEY AUTOINCREMENT,'
            '	"Guild"	TEXT NOT NULL,'
            '	"UserID"	INTEGER NOT NULL,'
            '	"Command"	TEXT NOT NULL,'
            '	"MessageContent"	TEXT NOT NULL,'
            '	"DateTime"	TEXT NOT NULL'
            ')'
        ]

        for table_sql in tables_sql:
            c = db.cursor()
            c.execute(table_sql)

    async def update_all_names(self):
        c = self.database.cursor()
        c.execute('SELECT * FROM Users')
        db_users = [DbUser(self.database, row=row) for row in c.fetchall()]

        for dbuser in db_users:
            user = self.get_user(dbuser.id)
            dbuser.Name = str(user)
            dbuser.update()
            await asyncio.sleep(0)

    async def update_currencies(self, increment=CURRENCY_GAIN_INCREMENT,
                                interval=CURRENCY_GAIN_INTERVAL):
        c = self.database.cursor()
        c.execute('SELECT * FROM Users')
        db_users = [DbUser(self.database, row=row) for row in c.fetchall()]

        for u in db_users:
            dt = datetime.datetime.now() - u.LastCurrencyGainedDateTime
            if dt > interval:
                missed = dt // interval
                u.LastCurrencyGainedDateTime += missed * interval
                u.AvailableCurrency += missed * increment
                u.update()
            await asyncio.sleep(0)

    def insert_guild_members(self, guild: discord.Guild):
        c = self.database.cursor()
        c.execute('SELECT * FROM Users')
        db_users = [DbUser(self.database, row=row) for row in c.fetchall()]
        for member in guild.members:
            assert (isinstance(member, discord.Member))
            insert_member(self.database, member, db_users=db_users)

    async def update_all(self, message: discord.Message):
        await self.update_all_names()
        await self.update_currencies()

        await message.channel.send('Update finished.')


def insert_member(db: sqlite3.Connection, member: discord.Member = None, server: discord.Guild = None, user_id=None,
                  db_users=None):
    if db_users is None:
        c = db.cursor()
        c.execute('SELECT ID, Name, ServerId, AvailableCurrency, LastCurrencyGainedDateTime FROM Users')
        db_users = [DbUser(db, row=row) for row in c.fetchall()]

    if member is None and user_id is not None:
        name = '<not filled>'
        user_id = user_id
    else:
        name = str(member)
        user_id = member.id

    if member.id not in [u.id for u in db_users]:
        u = DbUser(db)
        u.id = user_id
        u.Name = name
        u.LastCurrencyGainedDateTime = datetime.datetime.now()
        u.AvailableCurrency = 5000
        u.insert()
        return u
    else:
        return [u for u in db_users if u.id == member.id][0]


def date_to_db(date: datetime.datetime = epoch_time):
    return date.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


def db_to_date(string: str):
    try:
        return datetime.datetime.strptime(string + '000', '%Y-%m-%d %H:%M:%S.%f')
    except Exception as ex:
        print(datetime.datetime.now())
        print(ex)
        print(string + '000')
        raise


#  ############################# COMMANDS #############################################################################


async def add_bounty(message: discord.Message, db: sqlite3.Connection, client: discord.Client, **kwargs):
    """
    Adds reward to member from user's pool.
    :param db: database connection
    :param message: Requesting Message object.
    :param kwargs: {target: <user_id>, amount: <currency>}
    :return:
    """
    user = DbUser(db, user_id=message.author.id)
    target = DbUser(db, user_id=int(kwargs['target']))
    if kwargs['amount'] == 'all':
        amount = user.AvailableCurrency
    else:
        amount = int(kwargs['amount'])
    reason = kwargs['reason']

    if user.AvailableCurrency < amount:
        await message.channel.send(
            f'<@{message.author.id}> Not enough currency. You only have f{user.AvailableCurrency}:dollar:.'
        )
        return True

    else:
        user.AvailableCurrency -= amount
        user.LastRewardGivenDateTime = datetime.datetime.now()
        user.update()
        target.LastRewardGainedDateTime = datetime.datetime.now()
        target.CurrentPrize += amount
        target.update()
        db.cursor().execute(
            'INSERT INTO Transactions(User, Target, DateTime, Amount, Reason) VALUES (?, ?, ?, ?, ?)',
            [user.id, target.id, date_to_db(datetime.datetime.now()), amount, reason])
        db.commit()

        await message.channel.send(
            f'<@{user.id}> You just gave {amount} :dollar: to the reward pool.\n'
            f'<@{target.id}>\'s head is now worth {target.CurrentPrize}:dollar:!'
        )
        return True


async def profile_picture(message: discord.Message, __: sqlite3.Connection, client: discord.Client, **kwargs):
    """
    Displays full sized profile picture of either user or a mentioned member.
    :param __:
    :param message:
    :param kwargs:
    :return:
    """
    if kwargs['mention'] is None:
        user = message.author
    else:
        user = message.guild.get_member(int(kwargs['mention']))

    embed = discord.Embed(
        title=f'{user.name}\'s profile picture.',
        # description='{}\'s profile picture.'.format(user.mention) , color=0xecce8b
    )
    embed.set_image(url=user.avatar_url)
    await message.channel.send(
        '',
        embed=embed
    )
    return True


async def get_user_id(message: discord.Message, __: sqlite3.Connection, client: discord.Client, **kwargs):
    """
    Displays full sized profile picture of either user or a mentioned member.
    :param __:
    :param message:
    :param kwargs:
    :return:
    """
    if kwargs['mention'] is None:
        user = message.author
    else:
        user = message.guild.get_member(int(kwargs['mention']))

    await message.channel.send(
        f'{str(user)}\'s id: {user.id}'
    )
    return True


async def my_currency(message: discord.Message, db: sqlite3.Connection, client: discord.Client, **__):
    """
    Displays user's currency.
    :param db:
    :param message:
    :param __: kwargs
    :return:
    """

    user = DbUser(db, user_id=message.author.id)

    if not user.loaded:
        user = insert_member(db=db, member=message.author)

    await message.channel.send(f'<@{user.id}> You have {user.AvailableCurrency}:dollar:')
    return True


async def leaderboards(message: discord.Message, db: sqlite3.Connection, client: discord.Client, **kwargs) -> bool:
    """
    :param message:
    :param db:
    :param kwargs:
    :return:
    """

    c = db.cursor()
    c.execute('SELECT ID, CurrentPrize from Users WHERE CurrentPrize > 0 ORDER BY CurrentPrize desc')

    i = 1

    table = []

    for row in c.fetchall():
        member = message.guild.get_member(int(row[0]))
        if member is None:
            continue
        name = member.nick or member.display_name

        table.append((i, name, money_string(row[1])))

        i += 1

    pos_len = max([len(str(x)) for x, _, _ in table]) + 1
    name_len = max([len(str(x)) for _, x, _ in table]) + 1
    amount_len = max([len(str(x)) for _, _, x in table]) + 1

    ret_str = 'Leaderboards:\n'

    for pos, name, amount in table:
        ret_str += f'`{pos:>{pos_len}}.` `{name + ":":<{name_len}}` `{amount:>{amount_len}}` :dollar:\n'

    await message.channel.send(ret_str)
    return True


async def classic_release(message: discord.Message, db: sqlite3.Connection, client: discord.Client, **kwargs) -> bool:
    time_str = seconds_to_czech_string(
        (
                datetime.datetime.now() - datetime.datetime(year=2019, month=8, day=27, hour=00, minute=00)
        ).total_seconds())

    await message.channel.send(f'Classic je venku už {time_str}!')

    return True


async def love(message: discord.Message, db: sqlite3.Connection, client: discord.Client, **kwargs) -> bool:
    await message.channel.send(f'Miluje tě, jj')

    return True


async def add_reactor(message: discord.Message, db: sqlite3.Connection, client: discord.Client, **kwargs) -> bool:
    # await message.channel.send(f'Miluje tě, jj')

    return True


async def change_username(message: discord.Message, db: sqlite3.Connection, client: discord.Client, **kwargs) -> bool:
    if message.author.id != 143768570747289600:
        await message.channel.send(f'Only my rightful master can truly rename me!')

    else:
        await client.user.edit(username="Karel")
        await message.channel.send(f'Yes, master.')

    return True
    
    
def start_cubot():
    # global db, client

    client = Cubot(log_commands=True)

    client.addcom(
        Command(
            names=['profilepicture', 'profilepic', 'pp'],
            regexp=r'^__name__(\s*<@!?(?P<mention>\d*?)>)?$',
            command=profile_picture,
            usage='__author__ Usage: !profilepicture [@mention]',
            description='Displays profile picture of you or a mentioned user.'
        )
    )

    client.addcom(
        Command(
            names=['get_id'],
            regexp=r'^__name__(\s*<@!?(?P<mention>\d*?)>)?$',
            command=get_user_id,
            usage='__author__ Usage: !get_id [@mention]',
            description='Displays discord id of mentioned user. (For devs mainly.)'
        )
    )

    client.addcom(
        Command(
            names=['addbounty', 'ab'],
            regexp=r'^__name__ <@!?(?P<target>\d*?)>\s+(?P<amount>(?:\d+|all))(?:\s+(?P<reason>.*))?$',
            command=add_bounty,
            usage=f'__author__ Usage: !addbounty @user <amount> [reason]',
            description='Adds bounty to mentioned user.'
        )
    )

    client.addcom(
        Command(
            names=['currency', 'c'],
            regexp=r'^__name__( .*)?$',
            command=my_currency,
            usage=f'__author__ Usage: !currency',
            description='Displays your currency.'
        )
    )

    client.addcom(
        Command(
            names=['leaderboards', 'lb'],
            regexp=r'^__name__( .*)?$',
            command=leaderboards,
            usage=f'__author__ Usage: !leaderboards',
            description='Displays top 10 people ordered by their respective bounties.'
        )
    )

    client.addcom(
        Command(
            names=['classic'],
            regexp=r'^__name__( .*)?$',
            command=classic_release,
            usage=f'__author__ Usage: !classic',
            description='Displays time since release of Classic WoW in czech language.'
        )
    )

    client.addcom(
        Command(
            names=['love'],
            regexp=r'^__name__( .*)?$',
            command=love,
            usage=f'__author__ Usage: !love',
            description='Řekne jestli tě miluje.'
        )
    )

    client.addcom(
        Command(
            names=['change_username', 'cu'],
            regexp=r'^__name__ (?P<name>.*)$',
            command=change_username,
            usage=f'__author__ Usage: !change_username <username>',
            description='Changes the bot''s username.'
        )
    )

    client.run(open('token', 'r').read())


if __name__ == '__main__':
    try:
        p = Printer()
        print = p.print
        start_cubot()
    except Exception as exc:
        import builtins
        builtins.print("Fatal exception thrown:")
        builtins.print(exc)
        input()
