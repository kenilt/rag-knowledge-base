import marqo

from common import BASE_NAME


mq = marqo.Client()
result = mq.create_index(BASE_NAME)
print(result)
