#ifndef _TIMER_H
#define _TIMER_H

#if (ARDUINO >= 100)
# include <Arduino.h>
#else
# include <WProgram.h>
#endif

static const uint8_t TIMER_PB = 0;
static const uint8_t TIMER_IN = 1;

struct tcon_s {
	union {
		uint32_t val;
		struct {
			unsigned _unused:1;
			unsigned tcs:1;
			unsigned tsync:1;
			unsigned _spare:1;
			unsigned tckps:3;
			unsigned tgate:1;
			unsigned _space:3;
			unsigned twip:1;
			unsigned twdis:1;
			unsigned sidl:1;
			unsigned frz:1;
			unsigned on:1;
			unsigned _blank:16;
		};
	};
} __attribute__((packed));

class Timer {
	public:
		int _vec;
		int _irq;
		int _spl;
		int _ipl;
		volatile uint32_t *_pr;
        volatile uint32_t *_tmr;
		volatile tcon_s *_tcon;
		int _ps_size;
		
		Timer();
		void begin();
		void setFrequency(uint32_t f);
		void start();
		void stop();
		void attachInterrupt(void (*isr)());
		void detatchInterrupt();
        void setClockSource(uint8_t src);
        void setPrescaler(uint16_t ps);
        void setPeriod(uint32_t per);
        void reset();
        uint32_t getCount();
        uint32_t getAndResetCount();
        void enableGate();
        void disableGate();
};

class Timer1 : public Timer {
	public:
		Timer1();	
		Timer1(int);	
};

class Timer2 : public Timer {
	public:
		Timer2();	
		Timer2(int);	
};

class Timer3 : public Timer {
	public:
		Timer3();	
		Timer3(int);	
};

class Timer4 : public Timer {
	public:
		Timer4();	
		Timer4(int);
};

class Timer5 : public Timer {
	public:
		Timer5();	
		Timer5(int);
};

#ifdef __PIC32MZ__

class Timer6 : public Timer {
	public:
		Timer6();	
		Timer6(int);
};

class Timer7 : public Timer {
	public:
		Timer7();	
		Timer7(int);
};

class Timer8 : public Timer {
	public:
		Timer8();	
		Timer8(int);
};

class Timer9 : public Timer {
	public:
		Timer9();	
		Timer9(int);
};

#endif

#endif
