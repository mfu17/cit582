import math

def num_BTC(b):

    div = b // 210000
    cnt = b % 210000

    c = 210000*50*(1-0.5**div)/(1-0.5) + cnt*50*0.5**div
    return c


