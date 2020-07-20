from queue import Queue
from threading import Thread
from time import sleep
import logging
from datetime import date

from RPi import GPIO
from RPLCD.gpio import CharLCD
from gpiozero import TrafficLights, TonalBuzzer, Button
from requests import Session

from fmframework.net.network import Network, LastFMNetworkException

from ticker.display import DisplayItem

logger = logging.getLogger(__name__)

lcd_width = 16


class Ticker:
    def __init__(self,
                 lcd_rs,
                 lcd_e,
                 lcd_data,
                 buzzer_pin,
                 red_led_pin,
                 yellow_led_pin,
                 green_led_pin,
                 button_pins,

                 fm_username: str,
                 fm_key: str):
        self.lcd = CharLCD(numbering_mode=GPIO.BCM,
                           cols=lcd_width,
                           rows=2,
                           pin_rs=lcd_rs,
                           pin_e=lcd_e,
                           pins_data=lcd_data,
                           auto_linebreaks=True)
        self.leds = TrafficLights(red=red_led_pin, yellow=yellow_led_pin, green=green_led_pin, pwm=True)

        self.buzzer = TonalBuzzer(buzzer_pin)

        self.notif_button = Button(button_pins[0])
        self.notif_button.when_activated = self.handle_notif_click

        self.button2 = Button(button_pins[1])
        self.button2.when_activated = lambda: self.queue_text('hey', 'hey')

        self.button3 = Button(button_pins[2])
        self.button4 = Button(button_pins[3])

        self.idle_text = dict()

        self.notification_queue = Queue()
        self.display_queue = Queue()
        self.display_thread = Thread(target=self.display_worker, name='display', daemon=True)

        self.rsession = Session()
        self.fmnet = Network(username=fm_username, api_key=fm_key)

        self.puller_thread = Thread(target=self.puller_worker, name='puller', daemon=True)

    def start(self):
        logger.info('starting ticker')

        self.lcd.clear()
        self.display_thread.start()
        self.puller_thread.start()
        self.set_status(green=True)

    def set_status(self,
                   green: bool = False,
                   yellow: bool = False,
                   red: bool = False):
        self.leds.green.value = 1 if green else 0
        self.leds.yellow.value = 1 if yellow else 0
        self.leds.red.value = 1 if red else 0

    def handle_notif_click(self):
        if not self.notification_queue.empty():
            while not self.notification_queue.empty():
                self.display_queue.put(self.notification_queue.get())
            self.leds.red.off()
        else:
            self.queue_text('No Notifications', '', interrupt=True, time=2)

    def puller_worker(self):
        while True:

            try:
                total = self.fmnet.get_scrobble_count_from_date(input_date=date.today())

                logger.debug(f'loaded daily scrobbles {total}')

                self.queue_text('Scrobbles Today', total)
                self.idle_text['daily_scrobbles'] = DisplayItem('Scrobbles', str(total))
            except LastFMNetworkException as e:
                logger.exception(e)
                self.queue_text('Last.FM Error', f'{e.http_code}, {e.error_code}, {e.message}')

            sleep(30)

    def display_worker(self):
        while True:
            if not self.display_queue.empty():
                display_item = self.display_queue.get(block=False)
                logger.info(f'dequeued {display_item}, size {self.display_queue.qsize()}')

                self.write_display_item(display_item)

                self.display_queue.task_done()

            else:
                if len(self.idle_text) > 0:
                    for key, item in self.idle_text.items():
                        if self.display_queue.empty():
                            break

                        logger.debug(f'writing {key}')
                        self.write_display_item(item)

                else:
                    self.write_to_lcd(['Ticker...', ''])
            sleep(0.1)

    def write_display_item(self, display_item):
        """write display item to LCD now"""
        if display_item.message is None:
            display_item.message = ''

        if len(display_item.message) > lcd_width:
            buffer = [display_item.title, '']
            self.write_to_lcd(buffer)
            self.loop_string(display_item.message, buffer, row=1, iterations=display_item.iterations)
        else:
            buffer = [display_item.title, display_item.message]
            self.write_to_lcd(buffer)
            sleep(display_item.time)

    def queue_notification(self, title, message, wrap_line=False, iterations=2):
        logger.debug(f'queueing {title}/{message} {iterations} times, wrapped: {wrap_line}')
        self.notification_queue.put(DisplayItem(title, str(message), wrap_line, iterations))
        self.leds.red.pulse()

    def queue_text(self, title, message, wrap_line=False, time=5, iterations=2, interrupt=False):
        logger.debug(f'queueing {title}/{message} {iterations} times, wrapped: {wrap_line}')

        item = DisplayItem(title, str(message), wrap_line=wrap_line, iterations=iterations, time=time)
        if interrupt:
            self.write_display_item(item)
        else:
            self.display_queue.put(item)

    def write_to_lcd(self, framebuffer):
        """Write the framebuffer out to the specified LCD."""
        self.lcd.home()
        for row in framebuffer:
            self.lcd.write_string(row.ljust(lcd_width)[:lcd_width])
            self.lcd.write_string('\r\n')

    def loop_string(self, string, framebuffer, row, delay=0.4, iterations=2):
        padding = ' ' * lcd_width
        s = padding + string + padding
        for round_trip in range(iterations):
            for i in range(len(s) - lcd_width + 1):
                framebuffer[row] = s[i:i + lcd_width]
                self.write_to_lcd(framebuffer)
                sleep(delay)
