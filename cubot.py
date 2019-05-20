import discord
from discord.ext import tasks, commands
import sqlite3
import re
import datetime
import asyncio
import win32gui, win32con
import os

# todo: Clean up `db` mess.
# todo: Use async wrapper for sqlite3.
# todo: Document everything.
# todo: Forget about this project.
# todo: Server unique currency amount?

epoch_time = datetime.datetime.utcfromtimestamp(0)


class DbUser:
    id: int = 0
    Name: str = ''
    AvailableCurrency: int = 0
    CurrentPrize: int = 0
    LastRewardGivenDateTime: datetime.datetime = epoch_time
    LastRewardGainedDateTime: datetime.datetime = epoch_time
    LastCurrencyGainedDateTime: datetime.datetime = epoch_time

    def __init__(self, db: sqlite3.Connection, id=None, row=None):
        self.loaded = False
        self.db = db
        if hasattr(id, '__iter__'):
            row = id
            id = None
        if row is not None:
            self.fill_data(row)
        elif id is not None:
            self.load(id)

    def load(self, id: int):
        sql = 'SELECT ' \
              ' ID,' \
              ' Name,' \
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
        c.execute(sql, [id])
        row = c.fetchone()
        if row is not None:
            self.fill_data(row)
            return self
        else:
            self.fill_data(insert_member(self.db, id=id))

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
            self.AvailableCurrency = row[2]
            self.CurrentPrize = row[3]
            self.LastRewardGivenDateTime = db_to_date(row[4])
            self.LastRewardGainedDateTime = db_to_date(row[5])
            self.LastCurrencyGainedDateTime = db_to_date(row[6])

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
    def __init__(self, names, regexp, command, usage=None, description='', cmd_char='!'):
        self.cmd_char = cmd_char
        self.names = names
        self.command = command
        self.re_list = [re.compile(regexp.replace('__name__', cmd_char + name)) for name in names]
        self.usage = usage or f'Command is in wrong format: {self.re_list[0].pattern}'
        self.description = description

    def match(self, message: discord.Message):
        for name in self.names:
            if message.content.lower().startswith(self.cmd_char + name):
                return True
        else:
            return False

    def run(self, message: discord.Message):
        for re in self.re_list:
            match = re.match(message.content)
            if match is not None:
                break
        else:
            return message.channel.send(self.format_string(message=message, string=self.usage))

        return self.command(message, **match.groupdict())

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
            else:
                
                self.database = sqlite3.connect(database)
                self.init_database(self.database)

        self.log_commands = log_commands

        self.CURRENCY_GAIN_INCREMENT = currency_gain_increment
        self.CURRENCY_GAIN_INTERVAL = currency_gain_interval

        super(Cubot, self).__init__(*args, **kwargs)

    def addcom(self, command):
        self.commands.append(command)

    async def on_ready(self):
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

        for command in self.commands:
            if command.match(message):
                try:
                    await command.run(message)
                    if self.log_commands:
                        print(f'[{datetime.datetime.now()}][{message.guild.name}]{message.author}: {message.content}')
                except Exception as ex:
                    print(message.author)
                    print(message.content)
                    raise ex

    async def on_member_join(self, member: discord.Member):
        insert_member(self.database, member)
        pass

    async def loop_calls(self):
        await self.update_currencies()
        await asyncio.sleep(60*60)

    async def help(self, message: discord.Message):
        help_str = '```'
        help_str += 'Available commands:\n'

        max_command_len = max([len(c.names[0]) for c in self.commands])

        for command in self.commands:
            help_str += f'{command.names[0]:{max_command_len}}: {command.description}\n'

        help_str += '```'

        print(help_str)
        await message.channel.send(help_str)

    def init_database(self, db:sqlite3.Connection = None):
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
            ')'
            ,
            'CREATE TABLE "Users" ('
            '	"ID"	INTEGER NOT NULL UNIQUE,'
            '	"Name"	TEXT DEFAULT \'-\','
            '	"AvailableCurrency"	INTEGER DEFAULT 0,'
            '	"CurrentPrize"	INTEGER DEFAULT 0,'
            '	"LastRewardGivenDateTime"	TEXT DEFAULT \'1970-01-01 00:00:00.000\','
            '	"LastRewardGainedDateTime"	TEXT DEFAULT \'1970-01-01 00:00:00.000\','
            '	"LastCurrencyGainedDateTime"	TEXT DEFAULT \'1970-01-01 00:00:00.000\','
            '	PRIMARY KEY("ID")'
            ')'
            ,
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
            assert(isinstance(member, discord.Member))
            insert_member(self.database, member, db_users=db_users)

    async def update_all(self, message: discord.Message):
        await self.update_all_names()
        await self.update_currencies()

        await message.channel.send('Update finished.')


def insert_member(db: sqlite3.Connection, member: discord.Member = None, id=None, db_users=None):
    if db_users is None:
        c = db.cursor()
        c.execute('SELECT ID, Name, AvailableCurrency, LastCurrencyGainedDateTime FROM Users')
        db_users = [DbUser(db, row=row) for row in c.fetchall()]

    if member is None and id is not None:
        name = '<not filled>'
        id = id
    else:
        name = str(member)
        id = member.id

    if member.id not in [u.id for u in db_users]:
        u = DbUser(db)
        u.id = id
        u.Name = name
        u.LastCurrencyGainedDateTime = datetime.datetime.now()
        u.AvailableCurrency = 5000
        u.insert()
        return u
    else:
        return [u for u in db_users if u.id == member.id][0]


def date_to_db(date: datetime.datetime=epoch_time):
    return date.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


def db_to_date(string: str):
    try:
        return datetime.datetime.strptime(string + '000', '%Y-%m-%d %H:%M:%S.%f')
    except Exception as ex:
        print(ex)
        print(string + '000')
        raise


async def add_bounty(message: discord.Message, db: sqlite3.Connection, **kwargs):
    """
    Adds reward to member from user's pool.
    :param message: Requesting Message object.
    :param kwargs: {target: <user_id>, amount: <currency>}
    :return:
    """
    user = DbUser(db, id=message.author.id)
    target = DbUser(db, id=int(kwargs['target']))
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


async def profile_picture(message: discord.Message, db: sqlite3.Connection, **kwargs):
    """
    Displays full sized profile picture of either user or a mentioned member.
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


async def get_user_id(message: discord.Message, db: sqlite3.Connection, **kwargs):
    """
    Displays full sized profile picture of either user or a mentioned member.
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


async def my_currency(message: discord.Message, db: sqlite3.Connection, **kwargs):
    """
    Displays user's currency.
    :param db:
    :param message:
    :param kwargs:
    :return:
    """

    user = DbUser(db, id=message.author.id)

    if not user.loaded:
        user = insert_member(db=db, member=message.author)

    await message.channel.send(f'<@{user.id}> You have {user.AvailableCurrency}:dollar:')
    return True


async def leaderboards(message: discord.Message, db: sqlite3.Connection, **kwargs):
    """
    :param message:
    :param db:
    :param kwargs:
    :return:
    """

    c = db.cursor()
    c.execute('SELECT ID, CurrentPrize from Users WHERE CurrentPrize > 0 ORDER BY CurrentPrize desc')

    table = 'Leaderboards:\n'

    i = 1
    for row in c.fetchall():
        member = message.guild.get_member(int(row[0]))
        if member is None:
            continue
        name = member.nick or member.display_name
        table += f'{i:20}. {name}: {row[1]}:dollar:\n'
        i += 1

    await message.channel.send(table)
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
            regexp=r'^__name__.*$',
            command=my_currency,
            usage=f'__author__ Usage: !currency',
            description='Displays your currency.'
        )
    )

    client.addcom(
        Command(
            names=['leaderboards', 'lb'],
            regexp=r'^__name__.*$',
            command=leaderboards,
            usage=f'__author__ Usage: !leaderboards',
            description='Displays top 10 people ordered by their respective bounties.'
        )
    )

    # client.addcom(
    #     Command(
    #         names=['update'],
    #         regexp=r'^__name__.*$',
    #         command=update_all,
    #         usage=f'__author__ Usage: !update',
    #         description='Updates currencies manually.'
    #     )
    # )

    client.run(r'NDgyMTY4NzU1NjcwMDg5NzM4.XMv8Mw.OQlSYBDR7p1NEGV-AoEOfatWPjM')


if __name__ == '__main__':
    The_program_to_hide = win32gui.GetForegroundWindow()
    win32gui.ShowWindow(The_program_to_hide, win32con.SW_HIDE)

    start_cubot()
