import threading
import serial
import time
from get_com_list import get_coms_list
import statistics


class DeviceController(threading.Thread):
    SINGLE_PORT_MAX_SCAN_TIME = 2.0
    DEVICE_TAG  = 'ESP32TERM'
    def __init__(self):
        threading.Thread.__init__(self)
        self.stable_derative = 0.05
        self.COM = None
        self.line = None
        self.points= []
        self.time_stamps = []
        self.derivatives = []
        self.examinator_callback = None
        self.scanner_callback = None

    def set_examinator_callback(self, callback):
        self.examinator_callback = callback

    def set_scanner_callback(self,callback):
        self.scanner_callback = callback

    def get_com_length(self):
        return len(get_coms_list())

    def com_scanner(self):
        coms = get_coms_list()
        for com in coms:
            try:
                print('Scanning COM : {}'.format(com))
                ser = serial.Serial(timeout=0)
                t0 = time.time()
                ser.baudrate = 115200
                ser.port = com
                ser.open()
                data_gathered = []
                while  time.time() - t0 <  DeviceController.SINGLE_PORT_MAX_SCAN_TIME:
                    chars = ser.read(2000)
                    # print(chars)
                    data_gathered.append(chars)
                    # print(data_gathered)
                    # print( b''.join(data_gathered).decode('ASCII'))
                    if DeviceController.DEVICE_TAG in  b''.join(data_gathered).decode('ASCII'):
                        self.COM = com
                        return
            except Exception as e:
                print(str(e))
                pass
            self.scanner_callback()
        raise ValueError('COM_NOT_FOUND')

    def run(self):
        ser = serial.Serial()
        ser.baudrate = 115200
        ser.port = self.COM
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
        if self.examinator_callback is not None:
            self.examinator_callback(val, derivative)

class Examinator():
    __MINIMAL_TEST_TIME = 15.0
    __DERIVATIVE_EPSILON = 0.01
    __MAXIMAL_TEST_TIME = 240.0
    __N_LAST_DERIVATIVES = 10
    __N_LAST_RES  = 5
    __SAMPLES_PER_SECOND = 1.1363
    __DERATIVE_MEAN_EPSILON = 0.0005
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
            if not all( i > 0 for i in self.derivatives) and not all(i<0 for i in self.derivatives):
                if  abs(statistics.mean(self.derivatives[-Examinator.__N_LAST_DERIVATIVES:])) < Examinator.__DERATIVE_MEAN_EPSILON:
                    self._set_test_res()

    def _set_test_res(self,time_out= False):
        self.elapsed_time  = time.time() - self.start_time
        self.result = sum(self.points[-Examinator.__N_LAST_RES:])/Examinator.__N_LAST_RES
        self.f_timeout=time_out
        self.examination_finished = True
        if self.finished_callback is not None:
            self.finished_callback()

    def _add_point(self,val,derivative):
        mean_vals = 100
        if  len(self.derivatives) >= Examinator.__N_LAST_DERIVATIVES:
            mean_vals=statistics.mean(self.derivatives[-Examinator.__N_LAST_DERIVATIVES:])
        print('{} {} {}'.format(val,derivative,mean_vals))
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






