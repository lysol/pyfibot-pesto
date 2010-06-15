try:
    from pymblr import Api, TumblrError
    has_pymblr = True
except:
    print 'Error loading pymblr (or one of its dependencies).  Please install it.'
from time import sleep
import cgi    

def init(botconfig):
    global config
    config = botconfig.get("module_tumblr", None)

def command_tumbl(bot, user, channel, args):

    new_args = args.split(' ')

    tag_args = filter(
        lambda arg: arg[0] == '#'
        ,new_args
    )

    real_args = filter(
        lambda arg: arg[0] != '#'
        ,new_args
    )    

    try:
         api = Api(config['tumblr_group'], config['tumblr_email'], config['tumblr_password'])
         post = api.write_regular(body = cgi.escape(' '.join(real_args) + "\nposted by %s" % bot.factory.getNick(user)), tags = tag_args)
         print "%s posted some text to Tumblr. %s" % (bot.factory.getNick(user), post['url'])
         bot.say(channel, "Your post: %s" % post['url'])
    except TumblrError, e:
         bot.say(channel, "Your post didn't go through.  Feel free to try again, champ.")
         print e
    
    except Exception, e:
         #bot.say(channel, "Something horrible happened.")
         print e

def command_quote(bot, user, channel, args):
    if has_pymblr is None:
        boy.say(channel, "Tumblr module not running.")
        return
    
    new_args = args.split(' ')

    tag_args = filter(
        lambda arg: arg[0] == '#'
        ,new_args
    )
    
    real_args = filter(
        lambda arg: arg[0] != '#'
        ,new_args
    )
    
    # remove hash
    tag_args = [arg[1:] for arg in tag_args]
    
    print "real args: %s\ntag args: %s" % (real_args, tag_args)
    
    if len(real_args) == 1:
        # quote a single person
        last_said = bot.channel_log.last_said(channel, real_args[0]).to_string()
        if last_said != None:
            try:
                api = Api(config['tumblr_group'], config['tumblr_email'], config['tumblr_password'])
                post = api.write_regular(body = cgi.escape(last_said), tags = tag_args, slug = 'quote')
                print "Quoted %s as %s" % (bot.factory.getNick(user), post['url'])
                bot.say(channel, "Your quote: %s" % post['url'])
            except TumblrError, e:
                bot.say(channel, "That quote didn't go through because Tumblr returned a temporary error.")
            except Exception, e:
                #bot.say(channel, "Something horrible happened.")
                print e
    elif len(real_args) == 2:
        # Post an entire exchange
        exchange = bot.channel_log.exchange_set(channel, user, int(real_args[0]) + 1, int(real_args[1]))
        lines = [cgi.escape(item.to_string()) for item in exchange]
        lines.reverse()
        full_text = "<br />\n".join(lines)
        try:
            api = Api(config['tumblr_group'], config['tumblr_email'], config['tumblr_password'])
            post = api.write_regular(body = full_text, tags = tag_args, slug = 'quote')
            print "Posted exchange as %s" % (post['url'])
            bot.say(channel, "Your post: %s" % post['url'])
        except TumblrError, e:
            bot.say(channel, "That quote didn't work because of a temporary issue with Tumblr.  Make sure you adjust the line offset if you try this again.")
        except Exception, e:
            #bot.say(channel, "Something horrible happened.")
            print e

def handle_url(bot, user, channel, url, msg, times = 0):
    if has_pymblr is None:
        return

    new_args = msg.split(' ')

    tag_args = filter(
        lambda arg: arg[0] == '#'
        ,new_args
    )

    real_args = filter(
        lambda arg: arg[0] != '#'
        ,new_args
    ) 

    filtered_msg = ' '.join(real_args).replace(url,'').replace(':','')

    times = times + 1
    print "Attempting to post %s for the #%i time" % (url, times)
    config['exclude_users'] = []
    if channel not in config['exclude_channels'] and user not in config['exclude_users']:
        nick = bot.factory.getNick(user)
        api = Api(config['tumblr_group'], config['tumblr_email'], config['tumblr_password'])
        caption = '%s\nvia %s' % (filtered_msg, nick)
        try:
            try:
                urls = api.readurls()
                if url not in api.readurls():
                    post = api.autopost_url(url, caption, tag_args)
                    print "%s posted a %s to %s" % (nick, post['type'], post['url'])
            except TumblrError:
                post = api.autopost_url(url, caption, tag_args)
                print "%s posted a %s to %s" % (nick, post['type'], post['url'])

        except TumblrError, e:
            if (times < 4):
                print e
                print "Error encountered, trying it again."
                # try it again, a couple of times.
                sleep(5)
                handle_url(bot, user, channel, url, msg, times)
            else:
                print e
                #bot.say(channel, "Something horrible happened.")
