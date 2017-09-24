#!/usr/bin/python
from __future__ import print_function

import sys
import socket
import json
import random
import time

def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("production", 25000))
    return s.makefile('rw', 1)

def write(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read(exchange):
    return json.loads(exchange.readline())

def submit(exchange,t_t, symbol, orderType, price, number):
	orderID = random.randint(1, 10**5)
	write(exchange, {"type": t_t, "order_id": orderID, "symbol": symbol, "dir": orderType, "price": price, "size": number})

def trash_strat(priceVale, numberVale, priceValbz, numberValbz):
    can = priceVale * numberVale + 10
    number=min(numberValbz,numberVale)
    bz_value = priceValbz * number - 10
    vale_value = priceVale * number
    if vale_value>bz_value:
        return(1)
    elif bz_value>vale_value:
        return(0)
    return(23)

def etf_strat(gs_price,ms_price,wfc_price,xlf_price,b_price):
    if ((gs_price*2+ms_price*3+wfc_price*2+b_price*3)>1.01*(xlf_price*10+100)):
        return(1)
    if ((gs_price*2+ms_price*3+wfc_price*2+b_price*3)<0.99*(xlf_price*10+100)):
        return(0)
    return(23)


def main():
    v_tran = 0
    what = 0
    t_count = 0
    start_time=time.time()
    exchange = connect()
    write(exchange, {"type": "hello", "team": "DATAGODS"})
    hello_from_exchange = read(exchange)
    print("The exchange replied:", hello_from_exchange, file=sys.stderr)
    while(1):
        current_time=time.time()
        if current_time-start_time>90:
            start_time=current_time
            write(exchange, {"type": 'convert', "order_id":random.randint(1, 10**5) , "symbol": 'XLF', "dir": "BUY", "size": 50})
        message = read(exchange)
        type_of_order=message['type']
        if type_of_order == 'book':
	    symbol = message['symbol']
            if symbol == 'BOND':
                if len(message['sell']):
                    what+=1
                    b_price=message['sell'][0][0]
                    
                for sell_order in message['sell']:
                    if int(sell_order[0])<1000:
                            orderID=random.randint(1, 10**5)
                            write(exchange, {"type": "add", "order_id": orderID, "symbol": "BOND", "dir": "BUY", "price":sell_order[0] , "size": sell_order[1]})
                for buy_order in message['buy']:
                    if int(buy_order[0])>=1000:
                        orderID=random.randint(1, 10**5)
                        number_being_sold=buy_order[1]
                        write(exchange, {"type": "add", "order_id": orderID, "symbol": "BOND", "dir": "SELL", "price": buy_order[0], "size": number_being_sold})
            if symbol =='VALBZ':
                if len(message['sell']):
                    VALBZ_price=message['sell'][0][0]
                    VALBZ_number=message['sell'][0][1]
                    v_tran += 1

            if symbol == 'VALE':
                if len(message['sell']):
		    VALE_price=message['sell'][0][0]
                    VALE_number=message['sell'][0][1]
                    v_tran +=1
            if(v_tran == 2):
                v_trade=trash_strat(VALE_price,VALE_number,VALBZ_price,VALBZ_number)
                if v_trade==1:
                    submit(exchange, 'add','VALBZ', 'BUY', VALBZ_price, min(VALBZ_number,VALE_number))
                    submit(exchange, 'add','VALE', 'SELL', VALE_price, min(VALBZ_number,VALE_number))
                elif v_trade==0:
                    submit(exchange, 'add','VALE', 'BUY', VALE_price, min(VALBZ_number,VALE_number))
                    submit(exchange, 'add','VALBZ', 'SELL', VALBZ_price, min(VALBZ_number,VALE_number))
                v_tran = 0

            if symbol =='GS':
                if len(message['sell']):
                    gs_price=message['sell'][0][0]
                    what+=1
            if symbol =='MS':
                if len(message['sell']):
                    ms_price=message['sell'][0][0]
                    what+=1
            if symbol =='WFC':
                if len(message['sell']):
                    wfc_price=message['sell'][0][0]
                    what+=1
            if symbol =='XLF':
                if len(message['sell']):
                    xlf_price=message['sell'][0][0]
                    what+=1
            if what==5:
                what_do=etf_strat(gs_price,ms_price,wfc_price,xlf_price,b_price)
                if what_do==1:
                    submit(exchange, 'add','XLF', 'BUY', xlf_price, 5)
                    submit(exchange, 'add','GS', 'SELL', gs_price, 5)
                    submit(exchange, 'add','MS', 'SELL', ms_price, 5)
                    submit(exchange, 'add','WFC', 'SELL', wfc_price, 5)
                    submit(exchange, 'add','BOND', 'SELL', b_price, 5)
                if what_do==0:
                    submit(exchange, 'add','XLF', 'SELL', xlf_price, 5)
                    submit(exchange, 'add','GS', 'BUY', gs_price, 5)
                    submit(exchange, 'add','MS', 'BUY', ms_price, 5)
                    submit(exchange, 'add','WFC', 'BUY', wfc_price, 5)
                    submit(exchange, 'add','BOND', 'BUY', b_price, 5)
                what=0


        if type_of_order == 'fill':
            if message['symbol']=='BOND':
                if message['dir']== 'BUY':
                    print(message)
                if message['dir'] == 'SELL':
		    print(message)
            if (message['symbol']=='VALBZ' or message['symbol']=='VALE'):
                if message['dir']== 'BUY':
                    print(message)
                    write(exchange, {"type": 'convert', "order_id":random.randint(1, 10**5) , "symbol": message['symbol'], "dir": "SELL", "size": message['size']})
                    print('VALBZ AND VALE CONVERTED')
            if (message['symbol']=='XLF'):
                if message['dir']== 'BUY':
                    print(message)
                    write(exchange, {"type": 'convert', "order_id":random.randint(1, 10**5) , "symbol": message['symbol'], "dir": "SELL", "size": message['size']})
                    print('XLF CONVERTED due to buy signal')
                if message['dir']== 'SELL':
                    print(message)
                    write(exchange, {"type": 'convert', "order_id":random.randint(1, 10**5) , "symbol": message['symbol'], "dir": "BUY", "size": message['size']})
                    print('XLF CONVERTED due to sell signal')
	if type_of_order=='ack':
		print(message)
#	if type_of_order=='reject':
#		print(message)
	if type_of_order=='error':
		print(message)

if __name__ == "__main__":
    main()
