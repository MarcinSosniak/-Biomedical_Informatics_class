import serial.tools.list_ports




def get_com_str_from_object(com_obj):
    r_str  = str(com_obj)[::-1]
    idx = r_str.find('(')
    if idx == -1:
        raise ValueError('com scan found element without (comXXX) , \'(\'  was not found in string \'{}\''.format( r_str[::-1]))
    return (r_str[1:idx])



coms_str_base= list(map(lambda x: get_com_str_from_object(x)[::-1],list(serial.tools.list_ports.comports())))
print(coms_str_base) ## don't know why but it just works

def get_coms_list():
    return list(map(lambda x: get_com_str_from_object(x)[::-1],list(serial.tools.list_ports.comports())))