from slacker import Slacker

import tokens

class SlackBot(object):

	slack_connect = Slacker(tokens.TOKEN_SLACK)

	@classmethod
	def main(cls, user_id, message):
		cls.slack_connect.chat.post_message(user_id, 'Ответ на заданный вопрос: ' + message)


# if __name__ == '__main__':
# 	SlackBot.main()