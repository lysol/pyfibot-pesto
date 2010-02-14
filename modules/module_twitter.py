try:
    from twyt import twitter, data
    has_twyt = True
except:
    print 'Error loading twyt (or one of its dependencies).  Please install it.'

from twisted.internet import reactor
from time import strptime, mktime, localtime
from datetime import timedelta, datetime
import re

def command_quote(bot, user, channel, args):
    new_args = args.split(' ')

    tag_args = filter(
        lambda arg: arg[0] == '#'
        ,new_args
    )
    
    real_args = filter(
        lambda arg: arg[0] != '#'
        ,new_args
    )

    tag_args = ' '.join(tag_args)
    
    print "real args: %s\ntag args: %s" % (real_args, tag_args)
    
    if len(real_args) == 1:
        # quote a single person
        last_said = ' '.join(bot.channel_log.last_said(channel, real_args[0]).to_string().split(' ')[1:])
        if last_said != None:
            try:
                command_twit(bot, user, channel, "%s %s" % (last_said, tag_args) )
                print "Quoted %s to twitter" % real_args[0]
            except TumblrError, e:
                bot.say(channel, "That quote didn't go through because Tumblr is broke")
            except Exception, e:
                bot.say(channel, "Hey, esch, beer sucks")
                print e
    else:
        return
            

def command_twit(bot, user, channel, args):
    if has_twyt is None:
        bot.say(channe, "twyt or one of its dependences not installed. CANNOT COMPLY.")
    try:
        t = twitter.Twitter()
        t.set_auth(config['twitter_user'], config['twitter_password'])
        tweet = args
        if len(tweet) > 140:
            bot.say(channel, "josiah too long for josiah, by %i characters" % (len(tweet) - 140))
            return
        t.status_update(tweet)
    except Exception, e:
        bot.say(channel, "Something horrible happened and now I'm worried about having children.")
        print e
        return

def handle_timerEvent(bot, counter):
    if has_twyt is None:
        return
    if counter % 180 == 0 or counter == 0:
        timed_replies(bot)

def command_checkreplies(bot, user, channel, args):
    if has_twyt is None:
        bot.say(channel,"twyt or one of its dependencies not installed.  why you do this to me")
        return    
    if isAdmin(user):
        timed_replies(bot, True)

def timed_replies(bot, return_status = False, channel = ''):
    t = twitter.Twitter()
    t.set_auth(config['twitter_user'], config['twitter_password'])
    
    tweets = data.StatusList(t.status_replies())
    
    times = [strptime(tweet.created_at,'%a %b %d %H:%M:%S +0000 %Y') for tweet in tweets]
    #times.sort()
    max_time = times[0]
    
    for tweet in tweets:
        time_posted = strptime(tweet.created_at,'%a %b %d %H:%M:%S +0000 %Y')
        
        # reformat the reply.  Only remove the first mention of your bot's twitter account.
        new_text = '<%s> %s' % (tweet.user.screen_name, tweet.text.replace('@%s' % config['twitter_user'],'',1))
        
        if time_posted > localtime(config['last_tweet_time']):
            for channel in bot.network.channels:
                bot.say(channel, new_text)
    
    config['last_tweet_time'] = mktime(max_time)
    
    
    if return_status and channel in bot.network.channels:
        bot.say(channel, "Retrieved %i tweets." % len(tweets))

def command_sup(bot, user, channel, args):
    if has_twyt is not None and len(args.split(' ')) == 1:
        try:
            t = twitter.Twitter()
            t.set_auth(config['twitter_user'], config['twitter_password'])
            
            udict = data.simplejson.loads(t.user_show(id=args))
            tweet = "<%s> %s" % (udict['screen_name'], udict['status']['text'])
            bot.say(channel, tweet)
        except Exception, e:
            print e

def handle_url(bot, user, channel, url, msg):
    # handled pasted urls
    if 'twitter.com' in url and has_twyt is not None:
        try:
            t = twitter.Twitter()
            t.set_auth(config['twitter_user'], config['twitter_password'])
        
            url = re.sub('\/$','', url)
            post_id = url.split('/')[-1]
            status = data.Status()
            status.load_json(t.status_show(post_id))
            tweet = "<%s> %s" % (status.user.screen_name, status.text)
            bot.say(channel, tweet)
        except Exception, e:
            print e
    
def init(botconfig):
    global config
    config = botconfig.get("module_twitter", None)
