from tweepy.errors import Forbidden
from tweepy import OAuthHandler
from tweepy import API

from configobj import ConfigObj
from ast import literal_eval
from typing import Union

import sys


cfg = ConfigObj('static/config.cfg')

TOKENS = cfg.get('TOKENS')

USER = cfg.get('USER')

COMMENT = cfg.get('COMMENT')

MAILING = cfg.get('MAILING')
MESSAGE = cfg.get('MESSAGE')

UNSUBSCRIBE = cfg.get('UNSUBSCRIBE')
STOP = cfg.get('NUMBER')


def unsubscribe(bot: API, user: Union[int, list, set]) -> None:

    if isinstance(user, (list, set)):
        for user_id in user[0: int(STOP)]:
            bot.destroy_friendship(user_id=user_id)

    elif isinstance(user, int):
        bot.destroy_friendship(user_id=user)


def send_message(bot: API, user: Union[int, list, set], text: str) -> None:

    if isinstance(user, (list, set)):
        for user_id in user:
            bot.send_direct_message(user_id, text)

    elif isinstance(user, int):
        bot.send_direct_message(user, text)


def code(bot: API) -> None:
    tweets = bot.user_timeline(screen_name=USER, count=1)

    followers = bot.get_follower_ids(screen_name=USER)
    friends = bot.get_friend_ids(screen_name=USER)

    user_ids = set(followers + friends)


    if UNSUBSCRIBE.lower() == 'true':
        unsubscribe(bot, friends)
        sys.exit()

    if MAILING.lower() == 'true':
        send_message(bot, user_ids, MESSAGE)


    for tweet in tweets:
        try:
            tweet.favorite()
        except Forbidden:
            pass

        bot.update_status(
            status=COMMENT,
            in_reply_to_status_id=tweet.id,
            auto_populate_reply_metadata=True
        )


    for user_id in user_ids:
        bot.create_friendship(user_id=user_id)


def main() -> None:
    tokens = literal_eval(TOKENS)

    for api_key, api_secret, token, token_secret in tokens:

        auth = OAuthHandler(api_key, api_secret)
        auth.set_access_token(token, token_secret)

        bot = API(auth)
        code(bot)


if __name__ == '__main__':
    main()
