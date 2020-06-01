import threading
import serial
import time


class DeviceController(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stable_derative = 0.05
        self.COM = self._com_scanner()
        self.line = None
        self.points= []
        self.time_stamps = []
        self.derivatives = []
        self.callback = None

    def set_callback(self,callback):
        self.callback=callback
    def _com_scanner(self):
        return 'COM3'

    def run(self):
        ser = serial.Serial()
        ser.baudrate = 115200
        ser.port = 'COM3'
        ser.open()
        tmp_line = []
        while True:
            char = ser.read(1)

            if (char == b'\n'):
                self.line = b''.join(tmp_line).decode("ASCII")
                #print(self.line)
                tmp_line = []
                s_line = self.line.split()
                if len(s_line) == 3 and s_line[0]=='ESP32TERM':
                    current_val = float(s_line[1])
                    current_derative = float(s_line[2])
                    self._add_point(current_val,current_derative)
            else:
                tmp_line.append(char)


    def _add_point(self,val,derivative):
        self.points.append(val)
        self.time_stamps.append(time.time())
        self.derivatives.append(derivative)
        if self.callback is not None:
            self.callback(val,derivative)

class Examinator():
    __MINIMAL_TEST_TIME = 15.0
    __DERIVATIVE_EPSILON = 0.01
    __MAXIMAL_TEST_TIME = 60.0
    __N_LAST_DERIVATIVES = 10
    __N_LAST_RES  = 5
    __SAMPLES_PER_SECOND = 18.1818
    __MAXIMUM_PROGRESS_BAR_TICKS = int(__MAXIMAL_TEST_TIME * __SAMPLES_PER_SECOND) + 1

    def __init__(self):
        self.examination_finished = False
        self.examination_started = False
        self.points = []
        self.derivatives = []
        self.elapsed_time = 0.0
        self.result = 0.0
        self.start_time = None
        self.f_timeout = False
        self.progress_callback = None
        self.finished_callback = None
        self.clear()
        # self.examination_finished = False
        # self.examination_started = False
        # self.points = []
        # self.derivatives =[]
        # self.elapsed_time = 0.0
        # self.result = 0.0
        # self.start_time = None
        # self.f_timeout = False
        # self.progress_callback = None

    def get_callback(self):
        return self._call_back

    def _call_back(self,val,derivative):
        if not self.examination_started:
            return
        if self.examination_finished:
            return
        self._add_point(val,derivative)
        self._check_test_end_conditions()

    def _check_test_end_conditions(self):
        if time.time() - self.start_time < Examinator.__MINIMAL_TEST_TIME:
            return
        if time.time() - self.start_time > Examinator.__MAXIMAL_TEST_TIME:
            self._set_test_res(time_out=True)
            return
        if max(list(map(lambda x: abs(x),self.derivatives[-Examinator.__N_LAST_DERIVATIVES:]))) < Examinator.__DERIVATIVE_EPSILON:
            self._set_test_res()

    def _set_test_res(self,time_out= False):
        self.elapsed_time  = time.time() - self.start_time
        self.result = sum(self.points[-Examinator.__N_LAST_RES:])/Examinator.__N_LAST_RES
        self.f_timeout=time_out
        self.examination_finished = True
        if self.finished_callback is not None:
            self.finished_callback()

    def _add_point(self,val,derivative):
        print('{} {}'.format(val,derivative))
        self.points.append(val)
        self.derivatives.append(derivative)
        if self.progress_callback is not None:
            self.progress_callback()
        else:
            print('self.progress_callback is None')


    def clear(self):
        self.examination_finished = False
        self.examination_started = False
        self.points = []
        self.derivatives = []
        self.elapsed_time = 0.0
        self.result = 0.0
        self.start_time = None
        self.f_timeout = False
        self.progress_callback = None
        self.finished_callback = None

    def set_progress_callback(self,callback):
        self.progress_callback = callback
        # print('progress_call back set:')
        # print(callback)

    def progress_bar_max_ticks(self):
        return Examinator.__MAXIMUM_PROGRESS_BAR_TICKS

    def set_finished_callback(self,callback):
        self.finished_callback=callback

    def start_examination(self,f_clear = False):
        if self.examination_started:
            if f_clear:
                self.clear()
            else:
                raise ValueError("clear examination, before starting new one")
        self.start_time = time.time()
        self.examination_started = True

    def f_examination_finished(self):
        return self.examination_finished

    def get_elapsed_time(self):
        if not self.examination_finished:
            raise ValueError("call for test duration, test was not completed")
        return self.elapsed_time

    def get_res(self):
        if not self.examination_finished:
            raise ValueError("call for test result, test was not completed")
        return self.result

    def f_ended_with_timeout(self):
        if not self.examination_finished:
            raise ValueError("call for test result parameter, test was not completed")
        return self.f_timeout

    def get_current_test_time(self):
        if not self.examination_started:
            raise ValueError("call for test start parameter, test was not started")
        return time.time() - self.start_time

    def f_examination_started(self):
        return self.examination_started






