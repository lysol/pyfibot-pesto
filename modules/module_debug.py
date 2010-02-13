def init(botconfig):
    global config
    config = botconfig

def command_debug(bot, user, channel, args):
    if isAdmin(user):
        bot.say(channel,str(config))
    return

def command_exec(bot, user, channel, args):
    if isAdmin(user):
        env = config
        print args
        exec args
    return