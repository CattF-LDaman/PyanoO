import datetime

def give_default_datetime_string():

    return datetime.datetime.now().strftime("%d/%m/%Y @ %H:%M:%S")

def datetime_to_default_string(dt_obj):

    return dt_obj.strftime("%d/%m/%Y @ %H:%M:%S")

def datetime_from_default_string(dt_str):

    return datetime.datetime.strptime(dt_str,"%d/%m/%Y @ %H:%M:%S")