import os
from signal import pause

from ticker.ticker import Ticker

red_led_pin = 13
yellow_led_pin = 19
green_led_pin = 26

buzzer_pin = 7

button_pins = [21, 20, 16, 12]

lcd_rs = 18
lcd_e = 15
lcd_data = [14, 4, 3, 2]


def main():
    tick = Ticker(lcd_rs=lcd_rs,
                  lcd_e=lcd_e,
                  lcd_data=lcd_data,
                  buzzer_pin=buzzer_pin,
                  red_led_pin=red_led_pin,
                  yellow_led_pin=yellow_led_pin,
                  green_led_pin=green_led_pin,
                  button_pins=button_pins,

                  fm_username=os.environ.get('FM_USERNAME', 'sarsoo'),
                  fm_key=os.environ['FM_KEY'],

                  spot_client=os.environ['SPOT_CLIENT'],
                  spot_secret=os.environ['SPOT_SECRET'],
                  spot_refresh=os.environ['SPOT_REFRESH'])
    tick.start()


if __name__ == '__main__':
    main()
    pause()
