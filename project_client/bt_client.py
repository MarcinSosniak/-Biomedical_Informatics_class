from model import *



dc = DeviceController()
dc.start()


while True:
    void = input(">")
    examinator = Examinator()
    dc.set_examinator_callback(examinator.get_callback())
    print("starting examination")
    examinator.start_examination()
    while not examinator.f_examination_finished():
        time.sleep(1.0)
        print('test current time: {}'.format(examinator.get_current_test_time()))
    print('examination finished')
    print('examination res : {} '.format(examinator.get_res()))
    print('examination time : {} '.format(examinator.get_elapsed_time()))
    print('examination if timeout : {} '.format(examinator.f_ended_with_timeout()))
