from webhooks import webhook
from webhooks.senders import targeted

@webhook(sender_callable=targeted.sender)

def basic(url, wife, husband):
		return {"husband": husband, "wife": wife}
r = basic(url="http://httpbin.org/post", husband="Danny", wife="Audrey")

import pprint
pprint.pprint(r)