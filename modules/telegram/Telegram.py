import sys
is_64bits = sys.maxsize > 2**32
if is_64bits:
    print('64bit 환경입니다.')
else:
    print('32bit 환경입니다.')

import os
import configparser
from enum import Enum
import re
from telethon.tl.types import (PeerChannel)
from telethon import TelegramClient, events
from modules.trader.trader import Trader

class OrderStock:
    def __init__(self, code, code_name, type, value, percent=10):
        self.code = code
        self.code_name = code_name
        self.type = type
        self.value = value
        self.percent = percent

class TradeType(Enum):
    Buy = 1 # 매수
    Sell = 2 # 매도

class Telegram:
    def __init__(self):
        self.load_config()

        # Create the client and connect
        self.client = TelegramClient(self.username, self.api_id, self.api_hash)
        if not os.path.exists('session_name.session'):
            # 첫 실행: 전화번호와 코드 입력이 필요
            self.client.start()
        else:
            # 이미 저장된 세션만 로드
            self.client.connect()
            if not self.client.is_user_authorized():
                self.client.start()  # 첫 실행에만 prompt

        self.oldMsg = ""

        # self.broadcast_user_input_channel = self.broadcast_channel_url
        # if self.broadcast_user_input_channel.isdigit():
        #     self.broadEntity = PeerChannel(int(self.broadcast_user_input_channel))
        # else:
        #     self.broadEntity = self.broadcast_user_input_channel

        self.bot_channel = self.bot_channel_url
        if self.bot_channel.isdigit():
            self.bot_entity = PeerChannel(int(self.bot_channel))
        else:
            self.bot_entity = self.bot_channel

        # 유료방에서 그룹 채널로 브로드 캐스팅 한다.
        if self.channel_broadcast == True:
            @self.client.on(events.NewMessage(chats='[스탁나우] Golden Class'))
            async def handler(event):
                await self.client.send_message(entity=self.broadEntity, message=event.message.message)

        @self.client.on(events.NewMessage(chats='주식으로 은퇴하기'))
        async def retirement_handler(event):
            print("발신자 ID:", event.sender.id)

            msg = event.message.message
            result, info = self.proc_message(msg)
            if result:
                self.trade(info.type, info.code, info.code_name, info.value, info.percent)

        @self.client.on(events.NewMessage(chats=int(self.bot_channel_url)))
        async def handler(event):
       #     print("발신자 ID:", event.sender.id)

            msg = event.message.message
            result, info = self.proc_message(msg)
            if result is False:
                return

            ## 매수, 매도
            if info.type == TradeType.Buy:
                self.trader.buy(info.code, info.value, info.percent)
            else:
                self.trader.sell(info.code)

        self.trader = Trader()

        print("Telegram Bot Startup...")

    # Reading Configs
    def load_config(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini', encoding='utf-8')
        self.api_id = self.config['Telegram']['api_id']
        self.api_hash = self.config['Telegram']['api_hash']
        self.api_hash = str(self.api_hash)
        self.username = self.config['Telegram']['username']

        self.channel_broadcast = self.config['Telegram']['channel_broadcast'] == 'True'
        self.reading_channel_name = self.config['Telegram']['reading_channel_name']
        #self.broadcast_channel_name =self.config['Telegram']['broadcast_channel_name']
        #self.broadcast_channel_url = self.config['Telegram']['broadcast_channel_url']
        self.bot_channel_name = self.config['Telegram']['bot_channel_name']
        self.bot_channel_url = self.config['Telegram']['bot_channel_url']

        # self.kis_is_virtual = self.config['KIS']['virtual'] == 'True'
        # self.kis_id = self.config['KIS']['id']
        # self.kis_virutal_account = self.config['KIS']['virtual_account']
        # self.kis_virtual_app_key =self.config['KIS']['virtual_key']
        # self.kis_virtual_app_secret = self.config['KIS']['virtual_secret']
        # self.kis_real_account = self.config['KIS']['real_account']
        # self.kis_real_app_key =self.config['KIS']['real_key']
        # self.kis_real_app_secret = self.config['KIS']['real_secret']
        # self.seed_money = self.config['KIS']['seed_money']

    def Update(self):
        print("▶ 텔레그램 클라이언트 시작. 메시지 대기 중…")
        self.client.run_until_disconnected()


    async def _Update(self):
            await self.client.get_me()

    def trade(self, enum_trade_type, code, code_name, price, percent):
        print(f"TODO 여기다가 트레이드 정보 넣을것")
        message = '매수하였습니다'
        self.client.send_message(entity=self.broadEntity, message=message)

    def proc_message(self, msg: str):
        """
        텔레그램 메시지를 파싱하여
        code, code_name, tradeType, value, percent를 추출합니다.
        포맷이 맞지 않으면 False, None을 반환합니다.
        """
        if msg == self.oldMsg:
            return False, None
        self.oldMsg = msg

        print(f"---> telegram message: {msg}")
        print("-----------------------------------------------------")


        # 1. 신호(매수신호/매도신호)로 tradeType 결정
        sig = re.search(r'(\d{4}\.\d{1,2}\.\d{1,2})\s*(매수신호|매도신호)', msg)
        if not sig:
            return False, None

        date_str, signal = sig.group(1), sig.group(2)

        tradeType = (
            TradeType.Buy if signal == '매수신호'
            else TradeType.Sell
        )

        # 2. 종목명 추출 & 클린업
        nm = re.search(r'종목명\s*:\s*\[\s*([^\]]+?)\s*\]', msg)
        if not nm:
            return False, None
        raw_name = nm.group(1)
        # 대괄호, 공백 모두 제거
        code_name = re.sub(r'[\[\]\s]+', '', raw_name)

        # 3. 종목코드 추출
        cd = re.search(r'종목코드\s*:\s*(\d{6})', msg)
        if not cd:
            return False, None
        code = cd.group(1)

        # 4. 가격(value) 추출
        pv = re.search(r'(?:매수|매도)가\s*:\s*([\d,]+)\s*원', msg)
        if not pv:
            return False, None
        value = int(pv.group(1).replace(',', ''))

        # 5. 비중(percent) 추출
        p = re.search(r'비중\s*(\d+)%', msg)
        if not p:
            return False, None
        percent = int(p.group(1))

        print(f"MessageParser 결과 → 종목명: {code_name}, 코드: {code}, "
              f"유형: {tradeType.name}, 가격: {value}, 비중: {percent}%")
        print("-----------------------------------------------------")

        orderStock = OrderStock(
            code=code,
            code_name=code_name,
            type=tradeType,
            value=value,
            percent=percent
        )

        return True, orderStock

if __name__ == "__main__":
    telegram = Telegram()
    telegram.Update()
