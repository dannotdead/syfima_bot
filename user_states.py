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
