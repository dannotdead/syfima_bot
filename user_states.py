from enum import Enum


# Состояния пользователя
class States(Enum):
    S_START = '1' 
    S_QUESTION = '2'
    S_CHOOSE_LOC = '3'
    S_CHOOSE_LOC_VK = '3.1'
    S_CHOOSE_LOC_MAIL = '3.2'
    S_CHOOSE_LOC_SLACK = '3.3'
    S_FEEDBACK = '4'


    # def slack_send_webhook(self, text, channel, **kwargs):
    #     data = {
    #         'channel': channel,
    #         'text': text
    #     }
    #
    #     data.update(kwargs)
    #
    #     response = requests.post(
    #         url=tokens.SLACK_WEBHOOK,
    #         data=json.dumps(data),
    #         headers={'content-type': 'application/json'}
    #     )
    #
    #     pprint.pp(f'response from "send_webhook" {response.status_code}: {response.text}')
    #
    # def slack_post_msg(self, text, channel, as_user, **kwargs):
    #     data = {
    #         'token': tokens.TOKEN_SLACK,
    #         'channel': channel,
    #         'text': text,
    #         'as_user': as_user
    #     }
    #
    #     data.update(kwargs)
    #
    #     response = requests.post(
    #         url='https://slack.com/api/chat.postMessage',
    #         data=data
    #     )
    #
    #     pprint.pp(f'response from "send_webhook" {response.status_code}: {response.text}')