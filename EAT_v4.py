from numpy.core.einsumfunc import _einsum_path_dispatcher
import pandas as pd
import ccxt
import numpy as np
from datetime import datetime
import time
import smtplib
from email.mime.text import MIMEText

apiKey = 'Y3dcAaJ0BtLZdQpk9YTryEaft7wQQNMPZc7UJcZAGLKRbDFbtvw2GkRGVeadkvsL'
secKey = 'DA9aVE2d9fs7QWL6YfDs7Q3mJYHblnhJoPdO4tWjbDw4kGJCXviTSlZNroF99Dk9'



lastBol_low = 0.0
lastBol_high = 0.0
binanceFUTURE = ccxt.binance(config={
    'apiKey': apiKey,
    'secret': secKey,
    'enableRateLimit': True, 
})

binanceFR = ccxt.binance(config={
    'apiKey': apiKey, 
    'secret': secKey,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

markets = binanceFR.load_markets()
symbol = "ETH/USDT"
market = binanceFR.market(symbol)
leverage = 30

resp = binanceFR.fapiPrivate_post_leverage({
    'symbol': market['id'],
    'leverage': leverage
})


balance = binanceFUTURE.fetch_balance(params={"type": "future"})


def btcc(day):
    btc = binanceFR.fetch_ohlcv(
        symbol="ETH/USDT", 
        timeframe='5m', 
        since=None, 
        limit=24*12*day+26)


    return btc


def GetPD(day):
    dff = pd.DataFrame(btcc(day), columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    dff['datetime'] = pd.to_datetime(dff['datetime'], unit='ms')
    dff['open1'] = dff['open'].shift(1)
    dff['high1'] = dff['high'].shift(1)
    dff['low1'] = dff['low'].shift(1)
    dff['close1'] = dff['close'].shift(1)
    dff['volume1'] = dff['volume'].shift(1)
    dff.set_index('datetime', inplace=True)
    dff['tMA1'] = dff['close1'].rolling(window=20).mean()
    dff['tMA1'] = dff['tMA1'].round(2)
    dff['std1'] = dff['close1'].rolling(window=20).std()
    dff['tMA2'] = dff['tMA1'].shift(1)
    dff['ttMA1'] = dff['close1'].rolling(window=10).mean()
    dff['ttMA1'] = dff['ttMA1'].round(2)
    dff['ttMA2'] = dff['ttMA1'].shift(1)
    dff['mid'] = dff['open']/2 + dff['close']/2
    dff['mid1'] = dff['mid'].shift(1)
    dff['tend1'] = dff['ttMA1'] - dff['ttMA2']
    dff['tend2'] = dff['tend1'].shift(1)
    dff1= dff.dropna()
    dff1['bollow1'] = dff1['tMA1'] - 1.8*dff1['std1']
    dff1['bollow1'] = dff1['bollow1'].round(2)
    dff1['bolhigh1'] = dff1['tMA1'] + 1.8*dff1['std1']
    dff1['bolhigh1'] = dff1['bolhigh1'].round(2)
    dff1['mMm'] = dff1['mid'] - dff1['mid1']
    dff1.isnull().sum()
    return dff1


def mail(text,PN):
    now = datetime.now()
    
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login('pedrojang777@gmail.com','mpgzxiggfdjbarqz')

    msg =  MIMEText(text)
    msg['Subject'] = PN + str(now)

    s.sendmail('pedrojang777@gmail.com','peter000520@naver.com',msg.as_string())

    s.quit()

def nownow():
    now = datetime.now().minute

    return now

def nowhour():
    NH = datetime.now().hour

    return NH

# 선물 계좌 구하기 
def BGDF():
    balance = binanceFUTURE.fetch_balance(params={"type": "future"})

    return balance['USDT']['free']
# 현재가 구하기
def getcurrent():
    symbol = "ETH/USDT"
    btc = binanceFR.fetch_ticker(symbol)
    return btc['last']

def amountgetter():
    money = BGDF()
    if BGDF() > 30000:
        money = 30000
    amountget = round(money/getcurrent(),6)*0.985
    return amountget

#롱 - 풀매수 -
def buybit(a):
    order = binanceFR.create_market_buy_order(
    symbol=symbol,
    amount=a*leverage,
)

#숏 - 풀매도 -
def sellbit(a):
    order = binanceFR.create_market_sell_order(
    symbol=symbol,
    amount=a*leverage,
)

def buymethod3(i):
    stut1 = ls_oclo[i-3] >= ls_oclo[i-2] and ls_oclo[i-1] <= ls_oclo[i]  and (ls_oclo[i-2] <= ls_bollow[i-2]  or ls_oclo[i-1] <= ls_bollow[i-1])
    stut2 = False
    k = 1
    tendp = 0
    Alltendency = []
    while k <= 5:
        tendency = ls_tend1[i-k] - ls_tend2[i-k]
        Alltendency.append(tendency)
        if tendency > 0:
            tendp = tendp + 1
        k = k + 1
    
    if tendp >= 3 or sum(Alltendency) > 0:
        stut2 = True
    stut3 = stut2 or (Shortpossition == True)  # 고치기(로직 생각 잘 해서) 포지션이 있는 상태이면 stut2를 신경써서 매도 해야하고, 포지션이 있는 상태이면 신경쓰지 않고 매도해야함
    laststut = (stut1 and stut3)
    if Shortpossition == True:
        laststut = (stut1 and stut3) or sellnum * 0.98 > ls_close[i]
    # io = 0
    # ii = 0
    # while io <10:
    #     if ls_oclo[i+5-io] < ls_ma[i+5-io]:
    #         ii = ii + 1
    #     io = io + 1
    # if ii >= 7 and Shortpossition == True:
    #     laststut = False
    return laststut

def sellmethod3(i):
    stut1 = ls_ochi[i-3] <= ls_ochi[i-2] and ls_ochi[i-1] >= ls_ochi[i]  and (ls_ochi[i-2] >= ls_bolhigh[i-2] or ls_ochi[i-1] >= ls_bolhigh[i-1])
    stut2 = False
    k = 1
    tendp = 0
    Alltendency = []
    while k <= 5:
        tendency = ls_tend1[i-k] - ls_tend2[i-k]
        Alltendency.append(tendency)
        if tendency < 0:
            tendp = tendp + 1
        k = k + 1

    if tendp >= 3 or sum(Alltendency)<0:
        stut2 = True
    stut3 = stut2 or (Longpossition == True) # 고치기(로직 생각 잘 해서) 포지션이 있는 상태이면 stut2를 신경써서 매도 해야하고, 포지션이 있는 상태이면 신경쓰지 않고 매도해야함
    laststut = (stut1 and stut3)
    if Longpossition == True:
        laststut = (stut1 and stut3) or buynum * 1.02 < ls_close[i]
    # io = 0
    # ii = 0
    # while io <10:
    #     if ls_ochi[i+5-io] > ls_ma[i+5-io]:
    #         ii = ii + 1
    #     io = io + 1
    # if ii >= 7 and Longpossition == True:
    #     laststut = False
    return laststut


mail('Good luck!','Program started !!')

actiontime = -1
summary = ''
Shortpossition = False
Longpossition = False
nfornothing = 30000
MTG = False
ki = 0
while True:
    try:
        if nownow()%5 == 0:  # 5분마다 한번씩 행동하는 것 (3분으로 나누어 떨어지지 않을 시 행동하지 않음)
            if not(actiontime == nownow()):
                actiontime = nownow()
                etherinfo = GetPD(1)
                ls_mids = etherinfo.mid.tolist()
                ls_opens = etherinfo.open.tolist()
                ls_close = etherinfo.close.tolist()
                ls_mMm = etherinfo.mMm.tolist()
                ls_bollow = etherinfo.bollow1.tolist()
                ls_bolhigh = etherinfo.bolhigh1.tolist()
                ls_ma = etherinfo.tMA1.tolist()
                ls_tend1 = etherinfo.tend1.tolist()
                ls_tend2 = etherinfo.tend2.tolist()
                ls_high = etherinfo.high.tolist()
                ls_low = etherinfo.low.tolist()
                ls_vol =etherinfo.volume.tolist()
                ls_ochi = []
                ls_oclo = []
                i = 0
                while i < len(ls_opens):
                    if ls_opens[i] <= ls_close[i]:
                        ls_ochi.append(ls_close[i])
                        ls_oclo.append(ls_opens[i])
                    else:
                        ls_ochi.append(ls_opens[i])
                        ls_oclo.append(ls_close[i])
                    i = i + 1
                if MTG == False:
                    if sellmethod3(-2) == True:
                        if Shortpossition == False and Longpossition == False:
                            Shortpossition = True
                            beforetrade = BGDF()
                            sellnum = getcurrent()
                            PN = amountgetter()
                            sellbit(PN)
                            time.sleep(3)
                            summary = 'Long: ' + str(Longpossition) + ' | Short: '+ str(Shortpossition) + '| asset: '+ str(BGDF()) + ' |MTG : ' + str(MTG)
                            possition = 'Short possition'
                            mail(summary,possition)
                        if Longpossition == True:
                            Longpossition = False
                            sellnum = getcurrent()
                            sellbit(PN)
                            time.sleep(3)
                            aftertrade = BGDF()
                            time.sleep(3)
                            summary = 'Long: ' + str(Longpossition) + ' | Short: '+ str(Shortpossition) + '| asset: '+ str(BGDF()) + ' |MTG : ' + str(MTG)
                            possition = 'Long possition END'
                            mail(summary,possition)
                    if buymethod3(-2) == True:
                        if Shortpossition == False and Longpossition == False:
                            Longpossition = True
                            beforetrade = BGDF()
                            buynum = getcurrent()
                            PN = amountgetter()
                            buybit(PN)
                            time.sleep(3)
                            summary = 'Long: ' + str(Longpossition) + ' | Short: '+ str(Shortpossition) + '| asset: '+ str(BGDF()) + ' |MTG : ' + str(MTG)
                            possition = 'Long possition'
                            mail(summary,possition)
                        if Shortpossition == True:
                            Shortpossition = False
                            buynum = getcurrent()
                            buybit(PN)
                            time.sleep(3)
                            aftertrade = BGDF()
                            time.sleep(3)
                            summary = 'Long: ' + str(Longpossition) + ' | Short: '+ str(Shortpossition) + '| asset: '+ str(BGDF()) + ' |MTG : ' + str(MTG)
                            possition = 'Short possition END'
                            mail(summary,possition)
                    if Shortpossition == True and ls_vol[-2] > nfornothing and ls_close[-2] > ls_opens[-2]:
                        Shortpossition = False
                        buynum = getcurrent()
                        buybit(PN)
                        time.sleep(3)
                        Longpossition = True
                        beforetrade = BGDF()
                        buynum = getcurrent()
                        PN = amountgetter()
                        buybit(PN)
                        MTG = True
                        time.sleep(3)
                        summary = 'Long: ' + str(Longpossition) + ' | Short: '+ str(Shortpossition) + '| asset: '+ str(BGDF()) + ' |MTG : ' + str(MTG)
                        possition = 'something happened'
                        mail(summary,possition)
                    if Longpossition == True and ls_vol[-2] > nfornothing and ls_close[-2] < ls_opens[-2]:
                        Longpossition = False
                        sellbit(PN)
                        time.sleep(3)
                        Shortpossition = True
                        beforetrade = BGDF()
                        sellnum = getcurrent()
                        PN = amountgetter()
                        sellbit(PN)
                        MTG = True
                        time.sleep(3)
                        summary = 'Long: ' + str(Longpossition) + ' | Short: '+ str(Shortpossition) + '| asset: '+ str(BGDF()) + ' |MTG : ' + str(MTG)
                        possition = 'something happened'
                        mail(summary,possition)
                if MTG == True:
                    ki = ki + 1
        # if MTG == False:
        #     if Longpossition == True and getcurrent() > ls_bolhigh[-2]:
        #         sellbit(PN)
        #         sellnum = getcurrent()
        #         Longpossition = False
        #         mail(summary,possition)
        #     if Shortpossition == True and getcurrent() < ls_bollow[-2]:
        #         buybit(PN)
        #         buynum = getcurrent()
        #         Shortpossition = False
        #         mail(summary,possition)
        if MTG == True and ki > 7:
            if Longpossition == True and (ls_bolhigh[-2]*1.002<getcurrent()):
                Longpossition = False
                sellnum = getcurrent()
                sellbit(PN)
                aftertrade = BGDF()
                MTG = False
                summary = 'Long: ' + str(Longpossition) + ' | Short: '+ str(Shortpossition) + '| asset: '+ str(BGDF()) + ' |MTG : ' + str(MTG)
                possition = 'something happened'
                mail(summary,possition)
            if Shortpossition == True and (ls_bollow[-2]*1.002>getcurrent()):
                Shortpossition = False
                buynum = getcurrent()
                buybit(PN)
                aftertrade = BGDF()
                MTG = False
                summary = 'Long: ' + str(Longpossition) + ' | Short: '+ str(Shortpossition) + '| asset: '+ str(BGDF()) + ' |MTG : ' + str(MTG)
                possition = 'something happened'
                mail(summary,possition)
    except Exception as e:
       print(e)
       time.sleep(1)
#거래 시에는 sellmethod 와 buy method 에 -2 넣고 판단할것 (5분봉이 바뀐 즉시) ---------------------------------완료
# 현재 포지션에 맞는 거래 (숏 잡았을 시 정리 등 ) 고려하여 다시 작성
# 해야할것 -> 7시까지 거래내역을 누적하는 구조를 만들고 이를 7시에 전송하며 이를 하루마다 반복하는 프로그램 작성중 -------------- 완료 