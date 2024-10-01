import redis
import json
import math
from sympy import factorint

def prime_factors(n):
    f = factorint(n)
    factors_list = list(map(str, [factor for factor, count in f.items() for x in range(count)]))
    return factors_list

# Connect to Redis in the docker-compose network
r_db0 = redis.StrictRedis(host='redis', port=6379, db=0, password='66cfe2a89ba30e1a6c70680a')
r_db1 = redis.StrictRedis(host='redis', port=6379, db=1, password='66cfe2a89ba30e1a6c70680a')

pubsub = r_db0.pubsub()
pubsub.subscribe('hw3')

# print("Listening to channel 'hw3' on db 0...")

for message in pubsub.listen():
    if message['type'] == 'message':
        # print(f"Received message: {message['data']}")
        me = message['data']
        # decoded_data = me.decode('utf-8')
        data = json.loads(me)
        # print("Decoded JSON:", data)
        bignum = int(data['BIGNUM'])
        response_channel = data['CHANNEL']

        # print(prime_factors(bignum))
        # print("test")
        factors = prime_factors(bignum)
        # # print("test2")
        response = {
            "factors": factors,
            "value": str(bignum)
        }

        # print(response)
        r_db1.publish(response_channel, json.dumps(response))
        # # print(f"Sent factors {bignum} to channel {response_channel} on db 1.")
