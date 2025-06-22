import os
import math
from pykis import PyKis, KisBalance, KisOrder
from kis import load_pykis

class Trader:
    """
    kis(한국투자증권) 주식매매 클래스
    """
    def __init__(self ):
        """
        kis 데이터 초기화
        """
        is_virtual = os.getenv('PYKIS_IS_VIRTUAL')
        seed_money = os.getenv('SEED_MONEY')
        # print(f"[INIT] trader, is_virtual = {is_virtual}")

        if is_virtual:
            self.kis = load_pykis('virtual')
        else:
            self.kis = load_pykis('real')

        self.seed_money = int(seed_money)
        self.account = self.kis.account()
        self.account_no = self.account.account_number
        bal = self.get_balance()

        print(f"[INIT] trader, account_no = {self.account_no}, balance = {bal}, seed_money = {seed_money}")

    def get_balance(self) -> int:
        """
        계좌 잔액 조회
        :return: 잔액
        """
        balance: KisBalance = self.account.balance()
        krw_amount = balance.deposits['KRW'].amount
        return int(krw_amount)

    def get_balance_stock(self, code: str):
        """
        [Deprecated] 주식 보유 여부 체크
        :param code: 종목코드
        :return: boolean
        """
        balance: KisBalance = self.account.balance()

        for s in balance.stocks:
            # (1) 계좌번호 비교: s.account_number는 KisAccountNumber 객체
            acct_match = (
                    s.account_number.account_number
                    == balance.account_number.account_number
            )
            # (2) 심볼 비교
            symbol_match = (s.symbol == code)
            # (3) 수량 비교
            qty_match = (s.qty >= 1)

            if acct_match and symbol_match and qty_match:
                return True

        return False

    def calc_buy_qty(self, percent: int, price: int) -> int:
        """
        매수 수량, 가격을 계산
        percent: 시드 중 몇 %를 사용할지 (예: 10 → 10%)
        price:   현재 주가

        반환값: “원가에서 틱 단위로 3% 인상분에 가장 가깝게”
              맞춘 ‘마지노선 가격’ 기준 최대 매수 수량
        return : 매수수량, 가격
        """
        alloc_amount = self.seed_money * (percent / 100)

        # 1) 목표가(raw_price): 3% 인상
        raw_price = price * 1.03

        # 2) 원가에 따른 틱 사이즈
        tick = self.get_stock_tick_size(price)

        # 3) 원가에서 틱씩 올렸을 때 raw_price 이상인 첫 가격
        #    steps = 올려야 할 틱 개수 = ceil((raw_price - price) / tick)
        steps = math.ceil((raw_price - price) / tick)
        max_price = price + steps * tick

        # 4) 할당액으로 살 수 있는 수량
        qty = int(alloc_amount // max_price)

        # 5) 실제 잔고 한도 체크
        balance = int(self.get_balance())
        if balance < qty * max_price:
            qty = int(balance // max_price)

        return qty #, max_price
        #return qty, max_price

    def get_stock_tick_size(self, curValue):
        """
        가격 단위별 tick size 를 조회
        :param curValue: 가격
        :return: tick size(단위 호가)
        """
        if curValue < 1000: #0.1% 이상(최소 스프레드 비율)
            return 1
        elif 1000 <= curValue < 5000:    #0.1 ~ 0.5
            return 5
        elif 5000 <= curValue < 10000:   #0.2 ~ 0.1
            return 10
        elif 10000 <= curValue < 50000:  #0.5 ~ 0.1
            return 50
        elif 50000 <= curValue < 100000: #0.2 ~ 0.1
            return 100
        elif 100000 <= curValue < 500000:#0.5 ~ 0.1
            return 500
        elif 500000 <= curValue:  #0.2 이하
            return 1000

    def buy(self, code: str, price: int, percent: int):
        """
        매수 처리
        :param code: 종목코드
        :param price: 가격(None:시장가)
        :param percent: 비율
        :return:
        """

        stock = self.kis.stock(code)

        if stock is None:
            return False

        # 리더의 비중, 추천 가격 정보를 토대로, 매수할 수량과 금액(max)를 계산
        qty, max_price = self.calc_buy_qty(percent, price)

        if qty > 0:
            # kis.stock 으로 얻은 객체에 sell 호출
            # 시장가 매수 -> price(3% 이상 가격)
            order: KisOrder = stock.buy(price=max_price, qty=qty, condition=None, execution=None)
            return not order.pending

        return False

    # 매도
    def sell(self, code: str):

        #
        stock = self.kis.stock(code)

        if stock is not None:
            qty = int(stock.orderable)

            # 내가 가지고 있음
            if qty > 0:
                # kis.stock 으로 얻은 객체에 sell 호출
                # price=None (시장가)
                order: KisOrder = stock.sell(price=None, condition=None, execution=None)

                # 대기중인지 여부
                return not order.pending
            else:
                print(f"{code} 매도할 수량이 없습니다.")
                return False

        return True
