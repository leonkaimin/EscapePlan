import re


def quarter_to_months(quarter):
    if quarter is None:
        return None, None
    quarter_split = quarter.split('Q')
    y = quarter_split[0]
    q = int(quarter_split[1])-1

    return y, [f"{q*3+1}", f"{q*3+2}", f"{q*3+3}"]


def month_to_quart(m):
    if m is None:
        return None

    mat = re.match(r"(\S+)/(\S+)", m).groups()

    year = mat[0]
    quart = int((int(mat[1])-1)/3)+1
    return f"{year}Q{quart}"


def date_to_quarter(date):
    if '-' in date:
        date_split = date.split('-')
    elif '/' in date:
        date_split = date.split('/')
    y = date_split[0]
    m = date_split[1]
    # d = date_split[2]
    quarter = f"{y}Q{int((int(m)-1)/3)+1}"

    return quarter


def date_to_month(date):
    if '-' in date:
        date_split = date.split('-')
    elif '/' in date:
        date_split = date.split('/')
    y = date_split[0]
    m = date_split[1]
    # d = date_split[2]
    if int(m) < 10:
        return f"{y}/0{m}"
    else:
        return f"{y}/{m}"


def quarter_list(date1, date2):
    # print(date1)
    qlist = []
    if '-' in date1:
        date_split = date1.split('-')
    elif '/' in date1:
        date_split = date1.split('/')
    y = int(date_split[0])
    m = ((int(date_split[1])-1)/3)+1
    q2 = date_to_quarter(date2)
    q = None
    while q != q2:
        q = f"{y}Q{int(m)}"
        # print(q)
        qlist.append(q)
        m += 1
        if m > 4:
            y += 1
            m = 1

    return qlist
