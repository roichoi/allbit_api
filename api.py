from web3.auto import w3
from ethereum.tools import keys
import json
from eth_account.messages import defunct_hash_message
from rlp import decode
from eth_utils import (
    big_endian_to_int,
    decode_hex,
    encode_hex,
    int_to_big_endian,
    is_dict,
    is_string,
    keccak,
    remove_0x_prefix,
    to_dict,
    to_checksum_address
)
import requests

BASE_URL = None

def bigIntToHex(b):
	return hex(b).replace('L','')

def getPrivKey(keystore, pwd):
	if "data" in keystore['crypto']['kdfparams']['salt']:
		salt = keystore['crypto']['kdfparams']['salt']['data']
		salt_str = ""
		for h in salt:
			th = hex(h)[2:]
			if len(th) == 1:
				th = '0'+th
			salt_str = salt_str + th
		keystore['crypto']['kdfparams']['salt'] = salt_str
	privKey = w3.eth.account.decrypt(json.dumps(keystore), pwd)
	return encode_hex(privKey)

def pedding0(hexStr, bytesSize):
	if hexStr.startswith('0x'):
		hexStr = hexStr[2:]
	return "0x" + "0"*(bytesSize*2-len(hexStr)) + hexStr

def signMessage(wallet, apiKey, respList, pwd):
	messages = []
	for raw in respList:
		keystore = json.loads(raw['info']['keystore'])
		privKey = getPrivKey(keystore,pwd)
		actionHash = raw['info']['actionHash']
	    
		esMessage = w3.sha3("\x19Ethereum Signed Message:\n32".encode() + decode_hex(actionHash))
		signedMessage = w3.eth.account.signHash(esMessage, private_key=decode_hex(privKey))
		msg = {}
		msg['action'] = raw['info']['action']
		msg['actionHash'] = actionHash
		sig = {}
		sig['v'] = w3.toHex(signedMessage['v'])
		sig['r'] = pedding0(w3.toHex(signedMessage['r']),32)
		sig['s'] = pedding0(w3.toHex(signedMessage['s']),32)
		msg['message'] = json.dumps(sig)
		messages.append(msg) 

	r = requests.post(BASE_URL+"/open/v2/submit-signed-message/", data={'wallet':wallet, 'apiKey':apiKey, 'messages':json.dumps(messages)})

	return (r.text)



def getErrorJson(e):
	err = {'info':str(e), 'result':'fail'}
	return json.dumps(err)

def coinList():
	try:
		r = requests.post(BASE_URL+"/open/v2/coin-info-graph-list/", data={})
		r = r.text
	except Exception as e:
		r = getErrorJson(e)
	return r

def orderList(pairId):
	try:
		r = requests.post(BASE_URL+"/open/v2/coin/order-list/", data={'pair':pairId})
		r = r.text
	except Exception as e:
		r = getErrorJson(e)
	return r

def tradeList(pairId):
	try:
		r = requests.post(BASE_URL+"/open/v2/coin/trade-list/", data={'pair':pairId})
		r = r.text
	except Exception as e:
		r = getErrorJson(e)
	return r


def coinAmount(wallet, apiKey):
	try:
		r = requests.post(BASE_URL+"/open/v2/coin-amount/", data={'wallet':wallet, 'apiKey':apiKey})
		r = r.text
	except Exception as e:
		r = getErrorJson(e)
	return r

def runOrder(wallet, apiKey):
	try:
		r = requests.post(BASE_URL+"/open/v2/run-order-page/", data={'wallet':wallet, 'apiKey':apiKey})
		r = r.text
	except Exception as e:
		r = getErrorJson(e)
	return r

def orderStatus(orders):
	try:
		ordersJson = json.dumps(orders)
		r = requests.post(BASE_URL+"/open/v2/order-status/", data={'orders':ordersJson})
		r = r.text
	except Exception as e:
		r = getErrorJson(e)
	return r

def cancelOrder(wallet, apiKey, orders):
	try:
		strOrders = json.dumps(orders)
		r = requests.post(BASE_URL+"/open/v2/cancel-order/", data={'wallet':wallet, 'apiKey':apiKey, 'orders':strOrders})
		r = r.text
	except Exception as e:
		r = getErrorJson(e)
	return r
def generateOrder(wallet, apiKey, orders):
	try:
		strOrders = json.dumps(orders)		
		r = requests.post(BASE_URL+"/open/v2/generate-order/", data={'wallet':wallet, 'apiKey':apiKey, 'orders':strOrders})
		r = r.text
	except Exception as e:
		r = getErrorJson(e)
	return r



#r = coinList()
#print(r)

#r = orderList(pairId)
#print(r)

#r = tradeList(pairId)
#print(r)

#r = coinAmount(wallet, apiKey)
#print(r)

#r = runOrder(wallet, apiKey)
#print(r)

#r = orderStatus([orderHash])
#print(r)

'''
orders = []
order = {}
order['pair'] = 1
order['isSell'] = True
order['amount'] = "1000000000000000000" # amount * 10 ** token_decimals
order['price'] = "0.52000000"
orders.append(order)
r = generateOrder(wallet, apiKey, pwd, orders)
print(r)
'''

'''
orders = [orderHash]
r = cancelOrder(wallet, apiKey, orders)
print(r)
'''
