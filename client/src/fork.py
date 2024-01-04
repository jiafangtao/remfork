def make_request(data):
    req = dict()
    req['cmd'] = data.cmd
    req['wkdir'] = data.wkdir
    req['args'] = data.args

    return req