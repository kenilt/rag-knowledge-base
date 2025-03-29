import marqo

from util import BASE_NAME


mq = marqo.Client()
results = mq.index(BASE_NAME).delete()
print(results)
