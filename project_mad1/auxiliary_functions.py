import datetime

today=datetime.date.today()

def get_returndate(x):
    return_date=x + datetime.timedelta(days=8)
    return return_date

def allowed_file(filename):
    if '.pdf' in filename:
        return True
    return False

def allowed_img(name):
    if '.png' in name or '.jpg' in name or '.jpeg' in name:
        return True
    return False

def check_upi(x):
    if '@axl' in x or '@ibl' in x or '@ybl' in x or '@paytm' in x:
        return True
    return False