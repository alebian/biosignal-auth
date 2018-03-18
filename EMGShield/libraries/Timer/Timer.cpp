#include <Timer.h>

Timer::Timer() {
	// Constructor code here
	_tcon = NULL;
	_pr = NULL;
	_vec = 0;
	_irq = 0;
	_ipl = 0;
	_spl = 0;
    _tmr = NULL;
	_ps_size = 2;
}

void Timer::begin() {
	// Initialization code here
}

void Timer::setFrequency(uint32_t f) {
    uint32_t f_pb = getPeripheralClock();
	uint32_t baseclock = f_pb;
	uint8_t ps = 0;

	if (_ps_size == 2) {
		if (baseclock / f > 65535) {
			baseclock = f_pb / 8;
			ps = 1;
		}
	
	    if (baseclock / f > 65535) {
	        baseclock = f_pb / 64;
	        ps = 2;
	    }
	
	    if (baseclock / f > 65535) {
	        baseclock = f_pb / 256;
	        ps = 3;
	    }
	} else {
		if (baseclock / f > 65535) {
			baseclock = f_pb / 2;
			ps = 1;
		}
	
	    if (baseclock / f > 65535) {
	        baseclock = f_pb / 4;
	        ps = 2;
	    }
	
	    if (baseclock / f > 65535) {
	        baseclock = f_pb / 8;
	        ps = 3;
	    }
	
	    if (baseclock / f > 65535) {
	        baseclock = f_pb / 16;
	        ps = 4;
	    }
	
	    if (baseclock / f > 65535) {
	        baseclock = f_pb / 32;
	        ps = 5;
	    }
	
	    if (baseclock / f > 65535) {
	        baseclock = f_pb / 64;
	        ps = 6;
	    }
	
	    if (baseclock / f > 65535) {
	        baseclock = f_pb / 256;
	        ps = 7;
	    }
	}
	_tcon->tckps = ps;
	*_pr = baseclock / f;
}

void Timer::start() {
	_tcon->on = 1;
}


void Timer::stop() {
	_tcon->on = 0;
}

void Timer::attachInterrupt(void (*isr)()) {
	setIntVector(_vec, isr);
	setIntPriority(_vec, _ipl, _spl);
	clearIntFlag(_irq);
	setIntEnable(_irq);
}

void Timer::detatchInterrupt() {
	clearIntEnable(_irq);
	setIntPriority(_vec, 0, 0);
	clearIntVector(_vec);
}

void Timer::setClockSource(uint8_t src) {
    switch (src) {
        case TIMER_PB: _tcon->tcs = 0; break;
        case TIMER_IN: _tcon->tcs = 1; break;
    }
}

void Timer::reset() {
    *_tmr = 0;
}

uint32_t Timer::getCount() {
    return *_tmr;
}

uint32_t Timer::getAndResetCount() {
    uint32_t t = *_tmr;
    *_tmr = 0;
    return t;
}

void Timer::setPrescaler(uint16_t ps) {
    if (_ps_size == 2) {
        switch (ps) {
            case 1: _tcon->tckps = 0; break;
            case 8: _tcon->tckps = 1; break;
            case 64: _tcon->tckps = 2; break;
            case 256: _tcon->tckps = 3; break;
        }
    } else {
        switch (ps) {
            case 1: _tcon->tckps = 0; break;
            case 2: _tcon->tckps = 1; break;
            case 4: _tcon->tckps = 2; break;
            case 8: _tcon->tckps = 3; break;
            case 16: _tcon->tckps = 4; break;
            case 32: _tcon->tckps = 5; break;
            case 64: _tcon->tckps = 6; break;
            case 256: _tcon->tckps = 7; break;
        }
    }
}

void Timer::setPeriod(uint32_t per) {
    *_pr = per;
}

void Timer::enableGate() {
    _tcon->tgate = 1;
}

void Timer::disableGate() {
    _tcon->tgate = 0;
}

/****
 * The five timer instances. These are the classes which you 
 * should use for defining the timer in your sketch.
 ****/

Timer1::Timer1() {
	_vec = _TIMER_1_VECTOR;
#ifdef __PIC32MZ__
	_irq = _TIMER_1_VECTOR;
#else
	_irq = _TIMER_1_IRQ;
#endif
	_ipl = 4;
	_spl = 0;
	_tcon = (tcon_s *)&T1CON;
	_pr = (volatile uint32_t *)&PR1;
	_ps_size = 2;
    _tmr = (volatile uint32_t *)&TMR1;
}

Timer1::Timer1(int ipl) {
	_vec = _TIMER_1_VECTOR;
#ifdef __PIC32MZ__
	_irq = _TIMER_1_VECTOR;
#else
	_irq = _TIMER_1_IRQ;
#endif
	_ipl = ipl;
	_spl = 0;
	_tcon = (tcon_s *)&T1CON;
	_pr = (volatile uint32_t *)&PR1;
	_ps_size = 2;
    _tmr = (volatile uint32_t *)&TMR1;
}

Timer2::Timer2() {
	_vec = _TIMER_2_VECTOR;
#ifdef __PIC32MZ__
	_irq = _TIMER_2_VECTOR;
#else
	_irq = _TIMER_2_IRQ;
#endif
	_ipl = 4;
	_spl = 0;
	_tcon = (tcon_s *)&T2CON;
	_pr = (volatile uint32_t *)&PR2;
	_ps_size = 3;
    _tmr = (volatile uint32_t *)&TMR2;
}

Timer2::Timer2(int ipl) {
	_vec = _TIMER_2_VECTOR;
#ifdef __PIC32MZ__
	_irq = _TIMER_2_VECTOR;
#else
	_irq = _TIMER_2_IRQ;
#endif
	_ipl = ipl;
	_spl = 0;
	_tcon = (tcon_s *)&T2CON;
	_pr = (volatile uint32_t *)&PR2;
	_ps_size = 3;
    _tmr = (volatile uint32_t *)&TMR2;
}

Timer3::Timer3() {
	_vec = _TIMER_3_VECTOR;
#ifdef __PIC32MZ__
	_irq = _TIMER_3_VECTOR;
#else
	_irq = _TIMER_3_IRQ;
#endif
	_ipl = 4;
	_spl = 0;
	_tcon = (tcon_s *)&T3CON;
	_pr = (volatile uint32_t *)&PR3;
	_ps_size = 3;
    _tmr = (volatile uint32_t *)&TMR3;
}

Timer3::Timer3(int ipl) {
	_vec = _TIMER_3_VECTOR;
#ifdef __PIC32MZ__
	_irq = _TIMER_3_VECTOR;
#else
	_irq = _TIMER_3_IRQ;
#endif
	_ipl = ipl;
	_spl = 0;
	_tcon = (tcon_s *)&T3CON;
	_pr = (volatile uint32_t *)&PR3;
	_ps_size = 3;
    _tmr = (volatile uint32_t *)&TMR3;
}

Timer4::Timer4() {
	_vec = _TIMER_4_VECTOR;
#ifdef __PIC32MZ__
	_irq = _TIMER_4_VECTOR;
#else
	_irq = _TIMER_4_IRQ;
#endif
	_ipl = 4;
	_spl = 0;
	_tcon = (tcon_s *)&T4CON;
	_pr = (volatile uint32_t *)&PR4;
	_ps_size = 3;
    _tmr = (volatile uint32_t *)&TMR4;
}

Timer4::Timer4(int ipl) {
	_vec = _TIMER_4_VECTOR;
#ifdef __PIC32MZ__
	_irq = _TIMER_4_VECTOR;
#else
	_irq = _TIMER_4_IRQ;
#endif
	_ipl = ipl;
	_spl = 0;
	_tcon = (tcon_s *)&T4CON;
	_pr = (volatile uint32_t *)&PR4;
	_ps_size = 3;
    _tmr = (volatile uint32_t *)&TMR4;
}

Timer5::Timer5() {
	_vec = _TIMER_5_VECTOR;
#ifdef __PIC32MZ__
	_irq = _TIMER_5_VECTOR;
#else
	_irq = _TIMER_5_IRQ;
#endif
	_ipl = 4;
	_spl = 0;
	_tcon = (tcon_s *)&T5CON;
	_pr = (volatile uint32_t *)&PR5;
	_ps_size = 3;
    _tmr = (volatile uint32_t *)&TMR5;
}

Timer5::Timer5(int ipl) {
	_vec = _TIMER_5_VECTOR;
#ifdef __PIC32MZ__
	_irq = _TIMER_5_VECTOR;
#else
	_irq = _TIMER_5_IRQ;
#endif
	_ipl = ipl;
	_spl = 0;
	_tcon = (tcon_s *)&T5CON;
	_pr = (volatile uint32_t *)&PR5;
	_ps_size = 3;
    _tmr = (volatile uint32_t *)&TMR5;
}

#ifdef __PIC32MZ__

Timer6::Timer6() {
	_vec = _TIMER_6_VECTOR;
	_irq = _TIMER_6_VECTOR;
	_ipl = 4;
	_spl = 0;
	_tcon = (tcon_s *)&T6CON;
	_pr = (volatile uint32_t *)&PR6;
	_ps_size = 3;
    _tmr = (volatile uint32_t *)&TMR6;
}

Timer6::Timer6(int ipl) {
	_vec = _TIMER_6_VECTOR;
	_irq = _TIMER_6_VECTOR;
	_ipl = ipl;
	_spl = 0;
	_tcon = (tcon_s *)&T6CON;
	_pr = (volatile uint32_t *)&PR6;
	_ps_size = 3;
    _tmr = (volatile uint32_t *)&TMR6;
}

Timer7::Timer7() {
	_vec = _TIMER_7_VECTOR;
	_irq = _TIMER_7_VECTOR;
	_ipl = 4;
	_spl = 0;
	_tcon = (tcon_s *)&T7CON;
	_pr = (volatile uint32_t *)&PR7;
	_ps_size = 3;
    _tmr = (volatile uint32_t *)&TMR7;
}

Timer7::Timer7(int ipl) {
	_vec = _TIMER_7_VECTOR;
	_irq = _TIMER_7_VECTOR;
	_ipl = ipl;
	_spl = 0;
	_tcon = (tcon_s *)&T7CON;
	_pr = (volatile uint32_t *)&PR7;
	_ps_size = 3;
    _tmr = (volatile uint32_t *)&TMR7;
}

Timer8::Timer8() {
	_vec = _TIMER_8_VECTOR;
	_irq = _TIMER_8_VECTOR;
	_ipl = 4;
	_spl = 0;
	_tcon = (tcon_s *)&T8CON;
	_pr = (volatile uint32_t *)&PR8;
	_ps_size = 3;
    _tmr = (volatile uint32_t *)&TMR8;
}

Timer8::Timer8(int ipl) {
	_vec = _TIMER_8_VECTOR;
	_irq = _TIMER_8_VECTOR;
	_ipl = ipl;
	_spl = 0;
	_tcon = (tcon_s *)&T8CON;
	_pr = (volatile uint32_t *)&PR8;
	_ps_size = 3;
    _tmr = (volatile uint32_t *)&TMR8;
}

Timer9::Timer9() {
	_vec = _TIMER_9_VECTOR;
	_irq = _TIMER_9_VECTOR;
	_ipl = 4;
	_spl = 0;
	_tcon = (tcon_s *)&T9CON;
	_pr = (volatile uint32_t *)&PR9;
	_ps_size = 3;
    _tmr = (volatile uint32_t *)&TMR9;
}

Timer9::Timer9(int ipl) {
	_vec = _TIMER_9_VECTOR;
	_irq = _TIMER_9_VECTOR;
	_ipl = ipl;
	_spl = 0;
	_tcon = (tcon_s *)&T9CON;
	_pr = (volatile uint32_t *)&PR9;
	_ps_size = 3;
    _tmr = (volatile uint32_t *)&TMR9;
}

#endif
