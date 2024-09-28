
#include <stdio.h>

#include "pico/stdlib.h"
#include "hardware/pio.h"
#include "hardware/clocks.h"
#include "blink.pio.h"


#define PIO_BLINK_LED1_GPIO 3

extern unsigned char PULSES[];
extern unsigned int PULSES_LENGTH;
extern unsigned int WIDTHS[];
const uint SM=0;

int main() {
    // Underclock the PICO so it runs 35 times the speed of a Z80.
    // 3.5MHz * 35 = 122.5MHz
    set_sys_clock_khz(122500, true);
    stdio_init_all();
    sleep_ms(2000);

    PIO pio = pio0;

    pio_sm_claim(pio, SM);
    int offset = pio_add_program(pio, &pulse_program);
    pio_gpio_init(pio, PIO_BLINK_LED1_GPIO);
    pio_sm_set_consecutive_pindirs(pio, SM, PIO_BLINK_LED1_GPIO, 1, true);

    pio_sm_config sm_config = pulse_program_get_default_config(offset);
    sm_config_set_out_pins(&sm_config, PIO_BLINK_LED1_GPIO, 1);
    // Use a clock divide so 7 pio instructions exectute the same time a 1 Z80 t-state.
    sm_config_set_clkdiv_int_frac(&sm_config, 5, 0);
    pio_sm_init(pio, SM, offset, &sm_config);
    pio_sm_set_enabled(pio, SM, true);

    for (size_t i = 0; i < PULSES_LENGTH; ++i) {
        pio_sm_put_blocking(pio, SM, WIDTHS[PULSES[i]]);
    }

    while (true) {
        tight_loop_contents();
    }
}


