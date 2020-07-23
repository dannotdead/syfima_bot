from slacker import Slacker

import tokens
from standing.constants import *


class SlackBot(object):

	slack_connect = Slacker(tokens.TOKEN_SLACK)

	@classmethod
	def main(cls, user_id, message):
		cls.slack_connect.chat.post_message(user_id, REPLY + message)
