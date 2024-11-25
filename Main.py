import math
import os
import time
import certifi
from datetime import datetime, timedelta
from fyers_apiv3 import fyersModel
from fyers_apiv3.FyersWebsocket import data_ws
import TD_Setup.TD_Core as TD
import TD_Setup.TD_Breakout as TDBO
import TD_Setup.TD_Reversal as TDR
import TD_Setup.TD_SR_Levels as TDSR
import ALERT as alert
from Shoonya_Api import api as ShoonyaApi
from Shoonya_Api import PlaceOrder
from Shoonya_Api import ExitOrder
from Shoonya_Api import StopLimitOrder
from Logging import logger
from Fyers_Authentication.Fyers_Auto_Login import authentication

os.environ['SSL_CERT_FILE'] = certifi.where()


class TradingStrategy:
    def __init__(self):
        # --( STRATEGIES )-- #

        self.TDSR = True
        self.TDBO = False
        self.TDR = False

        # --( STRATEGIES )-- #

        self.fyers_data = self.init_fyers()
        self.MULTIPLAYER = 0.8
        self.RISK_TO_REWARD = 10
        self.BREAK_EVEN_POINT = 0.3
        self.LOT_SIZE = 25
        self.MAX_LOSS_CAP = 10
        self.EXPIRY = self.find_next_expiry()
        self.TDR_levels = {'SUPPORT': 0, 'RESISTANCE': 0, 'ATR': 0, 'buy_c': 0, 'sell_c': 0}
        self.TDBO_levels = {'SUPPORT': 0, 'RESISTANCE': 0, 'ATR': 0, 'counter': 0}
        self.TDSR_levels = {'SUPPORT': 0, 'RESISTANCE': 0, 'ATR': 0}

        # TDSR Strategy Variable
        self.TDSR_LONG = False
        self.TDSR_SHORT = False
        self.TDSR_ENTRY = 0
        self.TDSR_STOP_LOSS = 0
        self.TDSR_TARGET = 0
        self.TDSR_ORDER_ID = 0
        self.TDSR_prev_support = 0
        self.TDSR_prev_resistance = 0

        # TDBO Strategy Variable
        self.TDBO_LONG = False
        self.TDBO_SHORT = False
        self.TDBO_ENTRY = 0
        self.TDBO_STOP_LOSS = 0
        self.TDBO_TARGET = 0
        self.TDBO_ORDER_ID = 0
        self.TDBO_prev_support = 0
        self.TDBO_prev_resistance = 0

        # TDR Strategy Variable
        self.TDR_LONG = False
        self.TDR_SHORT = False
        self.TDR_ENTRY = 0
        self.TDR_STOP_LOSS = 0
        self.TDR_TARGET = 0
        self.TDR_ORDER_ID = 0
        self.TDR_prev_support = 0
        self.TDR_prev_resistance = 0

        self.sl_points = 0
        self.prev_minute = None
        self.print_flag = True
        self.margin_flag = False
        self.BREAK_EVEN_FLAG = False
        self.BREAK_EVEN_ORDER_ID = 0
        self.START_ALGO_FLAG = True

    def find_next_expiry(self):
        expiry_dates = [
            '08-08-2024', '14-08-2024', '22-08-2024', '29-08-2024', '05-09-2024',
            '26-09-2024', '31-10-2024', '26-12-2024', '27-03-2025', '26-06-2025',
            '24-12-2025', '25-06-2026', '31-12-2026', '24-06-2027', '30-12-2027',
            '29-06-2028', '28-12-2028', '28-06-2029'
        ]

        str_date = datetime.now().strftime('%Y-%m-%d')
        current_date = datetime.strptime(str_date, '%Y-%m-%d')

        expiry_dates_dt = [datetime.strptime(date, '%d-%m-%Y') for date in expiry_dates]

        # Find the next expiry date
        next_expiry_date = None
        for date in expiry_dates_dt:
            if date >= current_date:
                next_expiry_date = date
                break

        if next_expiry_date:
            # Convert the next expiry date to the desired format
            return next_expiry_date.strftime('%d%b%y').upper()
        else:
            return None

    # Example usage



    def init_fyers(self):
        try:
            with open('Fyers_Authentication/access_token', 'r') as file1:
                access_token = file1.readline().strip()
            client_id = "OVUPFX8VX5-100"
            return fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path="")
        except FileNotFoundError:
            logger.error("Access token file not found.")
            return None

    def prev_day(self, now):
        return (now - timedelta(days=4)).strftime('%d')

    def perform_task(self):
        global TDR_data_df, TDBO_data_df, TDSR_data_df
        now = datetime.now()
        historical_data_request = {
            "symbol": "NSE:NIFTY50-INDEX",
            "resolution": "1",
            "date_format": "1",
            "range_from": f"{now.strftime('%Y')}-{now.strftime('%m')}-{self.prev_day(now)}",
            "range_to": f"{now.strftime('%Y')}-{now.strftime('%m')}-{now.strftime('%d')}",
            "cont_flag": "1"
        }
        try:
            historical_data = self.fyers_data.history(data=historical_data_request)
            core_data = TD.create_dataframe(historical_data)
            core_data = TD.calculate_td_setup(core_data)

            # TDSR Strategy
            if self.TDSR:
                TDSR_data_df = TDSR.calculate_td_support_resistance(core_data)
                TDSR_data_df = TDSR.generate_trade_signals(TDSR_data_df, self.TDSR_levels, self.TDSR_LONG,
                                                           self.TDSR_SHORT, self.START_ALGO_FLAG)
                TDSR_data_df.to_csv('TDSR_output.csv', sep='\t', index=False)
                if self.print_flag:
                    self.TDSR_prev_support, self.TDSR_prev_resistance = self.TDSR_levels['SUPPORT'], self.TDSR_levels[
                        'RESISTANCE']

                self.START_ALGO_FLAG = False

            # TDBO Strategy
            if self.TDBO:
                TDBO_data_df = TDBO.calculate_td_support_resistance(core_data)
                TDBO_data_df = TDBO.generate_trade_signals(TDBO_data_df, self.TDBO_levels, self.TDBO_LONG,
                                                           self.TDBO_SHORT)
                TDBO_data_df.to_csv('TDBO_output.csv', sep='\t', index=False)
                if self.print_flag:
                    self.TDBO_prev_support, self.TDBO_prev_resistance = self.TDBO_levels['SUPPORT'], self.TDBO_levels[
                        'RESISTANCE']

            # TDR Strategy
            if self.TDR:
                TDR_data_df = TDR.calculate_td_support_resistance(core_data)
                TDR_data_df = TDR.generate_trade_signals(TDR_data_df, self.TDR_levels, self.TDR_LONG, self.TDR_SHORT)
                TDR_data_df.to_csv('TDR_output.csv', sep='\t', index=False)
                if self.print_flag:
                    self.TDR_prev_support, self.TDR_prev_resistance = self.TDR_levels['SUPPORT'], self.TDR_levels[
                        'RESISTANCE']

        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")

        if self.TDSR_prev_resistance != self.TDSR_levels['RESISTANCE'] or self.TDSR_prev_support != \
                self.TDSR_levels['SUPPORT']:
            self.TDSR_prev_support, self.TDSR_prev_resistance = self.TDSR_levels['SUPPORT'], self.TDSR_levels[
                'RESISTANCE']
            logger.info(
                f'TDSR Updated Support -( {self.TDSR_prev_support} )- | -( {self.TDSR_prev_resistance} )-')

        if self.TDBO_prev_resistance != self.TDBO_levels['RESISTANCE'] or self.TDBO_prev_support != \
                self.TDBO_levels['SUPPORT']:
            self.TDBO_prev_support, self.TDBO_prev_resistance = self.TDBO_levels['SUPPORT'], self.TDBO_levels[
                'RESISTANCE']
            logger.info(
                f'TDBO Updated Support -( {self.TDBO_prev_support} )- | -( {self.TDBO_prev_resistance} )-')

        if self.TDR_prev_resistance != self.TDR_levels['RESISTANCE'] or self.TDR_prev_support != self.TDR_levels[
            'SUPPORT']:
            self.TDR_prev_support, self.TDR_prev_resistance = self.TDR_levels['SUPPORT'], self.TDR_levels[
                'RESISTANCE']
            logger.info(
                f'TDR Updated Support -( {self.TDR_prev_support} )- | -( {self.TDR_prev_resistance} )-')

        candle_high = TDSR_data_df.at[len(TDSR_data_df) - 1, 'high']
        candle_low = TDSR_data_df.at[len(TDSR_data_df) - 1, 'low']
        candle_close = TDSR_data_df.at[len(TDSR_data_df) - 1, 'close']

        if self.TDSR_LONG:
            self.TDSR_STOP_LOSS = self.trailing_stops(self.TDSR_LONG, self.TDSR_SHORT, candle_high, candle_low,
                                                      candle_close,
                                                      self.TDSR_ENTRY, self.TDSR_STOP_LOSS, self.sl_points)
        elif self.TDSR_SHORT:
            self.TDSR_STOP_LOSS = self.trailing_stops(self.TDSR_LONG, self.TDSR_SHORT, candle_high, candle_low,
                                                      candle_close,
                                                      self.TDSR_ENTRY, self.TDSR_STOP_LOSS, self.sl_points)
        if self.TDBO_LONG:
            self.TDBO_STOP_LOSS = self.trailing_stops(self.TDBO_LONG, self.TDBO_SHORT, candle_high, candle_low,
                                                      candle_close,
                                                      self.TDBO_ENTRY, self.TDBO_STOP_LOSS, self.sl_points)
        elif self.TDBO_SHORT:
            self.TDBO_STOP_LOSS = self.trailing_stops(self.TDBO_LONG, self.TDBO_SHORT, candle_high, candle_low,
                                                      candle_close,
                                                      self.TDBO_ENTRY, self.TDBO_STOP_LOSS, self.sl_points)
        if self.TDR_LONG:
            self.TDR_STOP_LOSS = self.trailing_stops(self.TDR_LONG, self.TDR_SHORT, candle_high, candle_low,
                                                     candle_close,
                                                     self.TDR_ENTRY, self.TDR_STOP_LOSS, self.sl_points)
        elif self.TDR_SHORT:
            self.TDR_STOP_LOSS = self.trailing_stops(self.TDR_LONG, self.TDR_SHORT, candle_high, candle_low,
                                                     candle_close,
                                                     self.TDR_ENTRY, self.TDR_STOP_LOSS, self.sl_points)

    def onmessage(self, message):
        logger.info(message)
        global ORDER
        now = datetime.now()
        curr_time = now.strftime("%H:%M:%S")
        t = time.localtime()
        curr_sec = time.strftime('%S', t)

        if self.prev_minute != now.strftime("%H:%M"):
            if ShoonyaApi.get_order_book():
                if ShoonyaApi.get_order_book()[0].get('trantype') == 'B' and self.BREAK_EVEN_FLAG:
                    logger.warning(ShoonyaApi.get_order_book()[0])
                    self.TDSR_LONG = False
                    self.TDSR_SHORT = False
                    self.BREAK_EVEN_FLAG = False

            self.perform_task()
            # time.sleep(2)

            if self.print_flag:
                logger.info(f'---( ALGO STARTED )---')
                logger.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} --( 1 Min Data Get Updated )-- ")
                self.print_flag = False

            self.prev_minute = now.strftime("%H:%M")

        if 'ltp' in message:
            curr_price = message['ltp']
            # logger.info(curr_price)

            # if self.margin_flag:
            #     callOption = self.generate_Symbol(curr_price + 800, True, False)
            #     callOrder = ExitOrder(callOption)
            #     putOption = self.generate_Symbol(curr_price - 800, False, True)
            #     putOrder = ExitOrder(putOption)
            #     logger.success(callOrder)
            #     logger.success(putOrder)
            #     self.margin_flag = False

            if self.TDSR_LONG:
                if curr_time > "15:29:00" or curr_price <= self.TDSR_STOP_LOSS or curr_price >= self.TDSR_TARGET:
                    self.TDSR_LONG = False
                    if not (self.BREAK_EVEN_FLAG):
                        ORDER = ExitOrder(self.TDSR_ORDER_ID)
                    self.BREAK_EVEN_FLAG = False
                    logger.success(f'TDSR Trade Exited -> {ORDER}\nTime -( {curr_time} )- | Price -( {curr_price} )-')
                    alert.modifyed_orders('E', curr_price, " ", ' TDSR ')
                    time.sleep(60 - int(now.strftime("%S")))
                    self.perform_task()
            elif self.TDSR_SHORT:
                if curr_time > "15:29:00" or curr_price >= self.TDSR_STOP_LOSS or curr_price <= self.TDSR_TARGET:
                    self.TDSR_SHORT = False
                    if not (self.BREAK_EVEN_FLAG):
                        ORDER = ExitOrder(self.TDSR_ORDER_ID)
                    self.BREAK_EVEN_FLAG = False
                    logger.success(f'TDSR Trade Exited -> {ORDER}\nTime -( {curr_time} )- | Price -( {curr_price} )-')
                    alert.modifyed_orders('E', curr_price, " ", ' TDSR ')
                    time.sleep(60 - int(now.strftime("%S")))
                    self.perform_task()

            if self.TDBO_LONG:
                if curr_time > "15:28:00" or curr_price <= self.TDBO_STOP_LOSS or curr_price >= self.TDBO_TARGET:
                    self.TDBO_LONG = False
                    if not (self.BREAK_EVEN_FLAG):
                        ORDER = ExitOrder(self.TDBO_ORDER_ID)
                    self.BREAK_EVEN_FLAG = False
                    logger.success(f'TDBO Trade Exited -> {ORDER}\nTime -( {curr_time} )- | Price -( {curr_price} )-')
                    alert.modifyed_orders('E', curr_price, " ", ' TDBO ')
                    time.sleep(60 - int(now.strftime("%S")))
                    self.perform_task()
            elif self.TDBO_SHORT:
                if curr_time > "15:29:00" or curr_price >= self.TDBO_STOP_LOSS or curr_price <= self.TDBO_TARGET:
                    self.TDBO_SHORT = False
                    if not (self.BREAK_EVEN_FLAG):
                        ORDER = ExitOrder(self.TDBO_ORDER_ID)
                    self.BREAK_EVEN_FLAG = False
                    logger.success(f'TDBO Trade Exited -> {ORDER}\nTime -( {curr_time} )- | Price -( {curr_price} )-')
                    alert.modifyed_orders('E', curr_price, " ", ' TDBO ')
                    time.sleep(60 - int(now.strftime("%S")))
                    self.perform_task()

            if self.TDR_LONG:
                if curr_time > "15:28:00" or curr_price <= self.TDR_STOP_LOSS or curr_price >= self.TDR_TARGET:
                    self.TDR_LONG = False
                    if not (self.BREAK_EVEN_FLAG):
                        ORDER = ExitOrder(self.TDR_ORDER_ID)
                    self.BREAK_EVEN_FLAG = False
                    logger.success(f'TDR Trade Exited -> {ORDER}\nTime -( {curr_time} )- | Price -( {curr_price} )-')
                    alert.modifyed_orders('E', curr_price, " ", ' TDR ')
                    time.sleep(60 - int(now.strftime("%S")))
            elif self.TDR_SHORT:
                if curr_time > "15:28:00" or curr_price >= self.TDR_STOP_LOSS or curr_price <= self.TDR_TARGET:
                    self.TDR_SHORT = False
                    if not (self.BREAK_EVEN_FLAG):
                        ORDER = ExitOrder(self.TDR_ORDER_ID)
                    self.BREAK_EVEN_FLAG = False
                    logger.success(f'TDR Trade Exited -> {ORDER}\nTime -( {curr_time} )- | Price -( {curr_price} )-')
                    alert.modifyed_orders('E', curr_price, " ", ' TDR ')
                    time.sleep(60 - int(now.strftime("%S")))

            if not (self.TDSR_LONG or self.TDSR_SHORT) and self.TDSR:
                if curr_price > self.TDSR_levels['RESISTANCE']:
                    self.TDSR_LONG = True
                    self.TDSR_ORDER_ID = self.generate_Symbol(curr_price, self.TDSR_LONG, self.TDSR_SHORT)
                    logger.success(f'TDSR {self.TDSR_ORDER_ID}')
                    ORDER = PlaceOrder(self.TDSR_ORDER_ID)
                    logger.success(f'TDSR Order Executed -> {ORDER}\nTime -( {curr_time} )- | Price -( {curr_price} )-')
                    self.perform_task()
                    self.sl_points = min(round(self.TDSR_levels['ATR'] * self.MULTIPLAYER, 2), self.MAX_LOSS_CAP)
                    self.TDSR_ENTRY = curr_price
                    self.TDSR_STOP_LOSS = curr_price - self.sl_points
                    self.TDSR_TARGET = round(self.TDSR_ENTRY + (self.sl_points * self.RISK_TO_REWARD), 2)
                    alert.position_message(self.TDSR_LONG, self.TDSR_SHORT, self.TDSR_ENTRY, self.TDSR_STOP_LOSS,
                                           self.TDSR_TARGET, ' TDSR ')
                    self.TDSR_levels['RESISTANCE'] = float('inf')

                elif curr_price < self.TDSR_levels['SUPPORT']:
                    self.TDSR_SHORT = True
                    self.TDSR_ORDER_ID = self.generate_Symbol(curr_price, self.TDSR_LONG, self.TDSR_SHORT)
                    logger.success(f'TDSR {self.TDSR_ORDER_ID}')
                    ORDER = PlaceOrder(self.TDSR_ORDER_ID)
                    logger.success(f'TDSR Order Executed -> {ORDER}\nTime -( {curr_time} )- | Price -( {curr_price} )-')
                    self.perform_task()
                    self.sl_points = min(round(self.TDSR_levels['ATR'] * self.MULTIPLAYER, 2), self.MAX_LOSS_CAP)
                    self.TDSR_ENTRY = curr_price
                    self.TDSR_STOP_LOSS = self.TDSR_ENTRY + self.sl_points
                    self.TDSR_TARGET = round(self.TDSR_ENTRY - (self.sl_points * self.RISK_TO_REWARD), 2)
                    alert.position_message(self.TDSR_LONG, self.TDSR_SHORT, self.TDSR_ENTRY, self.TDSR_STOP_LOSS,
                                           self.TDSR_TARGET, ' TDSR ')
            #         self.TDSR_levels['SUPPORT'] = 0

            if not (self.TDBO_LONG or self.TDBO_SHORT) and self.TDBO:
                if curr_price > self.TDBO_levels['RESISTANCE']:
                    if self.TDBO_levels['counter'] == 0:
                        self.TDBO_LONG = True
                        self.TDBO_ORDER_ID = self.generate_Symbol(curr_price, self.TDBO_LONG, self.TDBO_SHORT)
                        logger.success(f'TDBO {self.TDBO_ORDER_ID}')
                        ORDER = PlaceOrder(self.TDBO_ORDER_ID)
                        logger.success(
                            f'TDBO Order Executed -> {ORDER}\nTime -( {curr_time} )- | Price -( {curr_price} )-')
                        self.perform_task()
                        self.sl_points = min(round(self.TDBO_levels['ATR'] * self.MULTIPLAYER, 2), self.MAX_LOSS_CAP)
                        self.TDBO_ENTRY = curr_price
                        self.TDBO_STOP_LOSS = curr_price - self.sl_points
                        self.TDBO_TARGET = round(self.TDBO_ENTRY + (self.sl_points * self.RISK_TO_REWARD), 2)
                        alert.position_message(self.TDBO_LONG, self.TDBO_SHORT, self.TDBO_ENTRY, self.TDBO_STOP_LOSS,
                                               self.TDBO_TARGET, ' TDBO ')
                    self.TDBO_levels['RESISTANCE'] = float('inf')

                elif curr_price < self.TDBO_levels['SUPPORT']:
                    if self.TDBO_levels['counter'] == 0:
                        self.TDBO_SHORT = True
                        self.TDBO_ORDER_ID = self.generate_Symbol(curr_price, self.TDBO_LONG, self.TDBO_SHORT)
                        logger.success(f'TDBO {self.TDBO_ORDER_ID}')
                        ORDER = PlaceOrder(self.TDBO_ORDER_ID)
                        logger.success(
                            f'TDBO Order Executed -> {ORDER}\nTime -( {curr_time} )- | Price -( {curr_price} )-')
                        self.perform_task()
                        self.sl_points = min(round(self.TDBO_levels['ATR'] * self.MULTIPLAYER, 2), self.MAX_LOSS_CAP)
                        self.TDBO_ENTRY = curr_price
                        self.TDBO_STOP_LOSS = self.TDBO_ENTRY + self.sl_points
                        self.TDBO_TARGET = round(self.TDBO_ENTRY - (self.sl_points * self.RISK_TO_REWARD), 2)
                        alert.position_message(self.TDBO_LONG, self.TDBO_SHORT, self.TDBO_ENTRY, self.TDBO_STOP_LOSS,
                                               self.TDBO_TARGET, ' TDBO ')
                    self.TDBO_levels['SUPPORT'] = 0

            if not (self.TDR_LONG or self.TDR_SHORT) and self.TDR:
                if curr_price > self.TDR_levels['RESISTANCE']:
                    if 0 <= self.TDR_levels['buy_c'] < 3:
                        self.TDR_LONG = True
                        self.TDR_ORDER_ID = self.generate_Symbol(curr_price, self.TDR_LONG, self.TDR_SHORT)
                        logger.success(f'TDR - {self.TDR_ORDER_ID}')
                        ORDER = PlaceOrder(self.TDR_ORDER_ID)
                        logger.success(
                            f'TDR Order Executed -> {ORDER}\nTime -( {curr_time} )- | Price -( {curr_price} )-')
                        self.perform_task()
                        self.sl_points = min(round(self.TDR_levels['ATR'] * self.MULTIPLAYER, 2), self.MAX_LOSS_CAP)
                        self.TDR_ENTRY = curr_price
                        self.TDR_STOP_LOSS = curr_price - self.sl_points
                        self.TDR_TARGET = round(self.TDR_ENTRY + (self.sl_points * self.RISK_TO_REWARD), 2)
                        alert.position_message(self.TDR_LONG, self.TDR_SHORT, self.TDR_ENTRY, self.TDR_STOP_LOSS,
                                               self.TDR_TARGET, ' TDR ')
                    self.TDR_levels['RESISTANCE'] = float('inf')

                elif curr_price < self.TDR_levels['SUPPORT']:
                    if 0 <= self.TDR_levels['sell_c'] < 3:
                        self.TDR_SHORT = True
                        self.TDR_ORDER_ID = self.generate_Symbol(curr_price, self.TDR_LONG, self.TDR_SHORT)
                        logger.success(f'TDR {self.TDR_ORDER_ID}')
                        ORDER = PlaceOrder(self.TDR_ORDER_ID)
                        logger.success(f'TDR Executed -> {ORDER}\nTime -( {curr_time} )- | Price -( {curr_price} )-')
                        self.perform_task()
                        self.sl_points = min(round(self.TDR_levels['ATR'] * self.MULTIPLAYER, 2), self.MAX_LOSS_CAP)
                        self.TDR_ENTRY = curr_price
                        self.TDR_STOP_LOSS = self.TDR_ENTRY + self.sl_points
                        self.TDR_TARGET = round(self.TDR_ENTRY - (self.sl_points * self.RISK_TO_REWARD), 2)
                        alert.position_message(self.TDR_LONG, self.TDR_SHORT, self.TDR_ENTRY, self.TDR_STOP_LOSS,
                                               self.TDR_TARGET, ' TDR ')
                    self.TDR_levels['SUPPORT'] = 0

    def onerror(self, message):
        # print('error')
        logger.error("Error: %s", message)

    def onclose(self, message):
        logger.info("Connection closed: %s", message)

    def onopen(self):
        data_type = "SymbolUpdate"
        symbols = ['NSE:NIFTY50-INDEX']
        self.fyers.subscribe(symbols=symbols, data_type=data_type)
        self.fyers.keep_running()

    def connect(self):
        self.fyers = data_ws.FyersDataSocket(
            access_token=self.fyers_data.token,
            log_path="",
            litemode=True,
            write_to_file=False,
            reconnect=True,
            on_connect=self.onopen,
            on_close=self.onclose,
            on_error=self.onerror,
            on_message=self.onmessage
        )
        self.fyers.connect()

    def trailing_stops(self, long, short, candle_high, candle_low, candle_close, entry, stop_loss, sl_points):
        if long:
            for rr in [10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5, 2, 1.5, 1]:
                if (candle_high - entry) > (sl_points * rr):
                    new_stop_loss = entry + (sl_points * (rr - 0.5))
                    if not (candle_close <= new_stop_loss):
                        if new_stop_loss > stop_loss:
                            if self.BREAK_EVEN_FLAG:
                                cancel_order = ShoonyaApi.cancel_order(self.BREAK_EVEN_ORDER_ID)
                                logger.warning(f' ORDER CANCLE -( {cancel_order} )-')
                                self.BREAK_EVEN_FLAG = False
                            alert.modifyed_orders("SLM", round(new_stop_loss, 2), f'1 : {rr - 0.5}')
                            return new_stop_loss
            if (candle_close - entry) > (sl_points * self.BREAK_EVEN_POINT):
                if entry > stop_loss:
                    price = float(ShoonyaApi.get_order_book()[0].get('avgprc'))
                    SLM_order = StopLimitOrder(price, self.TDSR_ORDER_ID)
                    self.BREAK_EVEN_FLAG = True
                    self.BREAK_EVEN_ORDER_ID = SLM_order.get('norenordno')
                    alert.modifyed_orders("SLM", round(entry, 2), 'Break Even')
                    return entry
            return stop_loss

        elif short:
            for rr in [10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5, 2, 1.5, 1]:
                if (entry - candle_low) > (sl_points * rr):
                    new_stop_loss = entry - (sl_points * (rr - 0.5))
                    if not (candle_close >= new_stop_loss):
                        if new_stop_loss < stop_loss:
                            if self.BREAK_EVEN_FLAG:
                                cancel_order = ShoonyaApi.cancel_order(self.BREAK_EVEN_ORDER_ID)
                                logger.warning(f' ORDER CANCLE -( {cancel_order} )-')
                                self.BREAK_EVEN_FLAG = False
                            alert.modifyed_orders("SLM", round(new_stop_loss, 2), f'1 : {rr - 0.5}')
                            return new_stop_loss
            if (entry - candle_close) > (sl_points * self.BREAK_EVEN_POINT):
                if entry < stop_loss:
                    price = float(ShoonyaApi.get_order_book()[0].get('avgprc'))
                    SLM_order = StopLimitOrder(price, self.TDSR_ORDER_ID)
                    self.BREAK_EVEN_FLAG = True
                    self.BREAK_EVEN_ORDER_ID = SLM_order.get('norenordno')
                    alert.modifyed_orders("SLM", round(entry, 2), 'Break Even')
                    return entry
            return stop_loss

    def generate_Symbol(self, curr_price, LONG, SHORT):
        # spot_price = round(curr_price / 50) * 50
        if LONG:
            spot_price = (math.floor((curr_price / 50)) * 50)
            return f'NIFTY{self.EXPIRY}P{spot_price}'
        elif SHORT:
            spot_price = (math.ceil((curr_price / 50)) * 50)
            return f'NIFTY{self.EXPIRY}C{spot_price}'


def curr_time():
    now = datetime.now()
    return now.strftime('%H:%M:%S')




# while True:
#     if curr_time() >= '09:15:00':
#         access_token = authentication()
#         file1 = open("Fyers_Authentication/access_token", "w")  # append mode
#         file1.write(access_token)
#         file1.close()
#         logger.success("Access_Token Genereted Successfully !!")
#         alert.server_alrt("Access_Token Genereted Successfully !!")
#         time.sleep(3)
#         break
#     time.sleep(10)
#
#
# time.sleep(3)

strategy = TradingStrategy()
strategy.connect()

# logger.success("Server Connected Successfully !!")
# alert.server_alrt("Server Connected Successfully !!")
