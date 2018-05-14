import subprocess
import time

import core.helper as core

PRODUCTION_CHAIN = 'production.pkl'
CONSUMPTION_CHAIN = 'consumption.pkl'
JSON = 'configFun/local/producer.json'
RESIN_DEVICE_UUID = '734e348be116e254fcc7a6f46708e96a'
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MzQwNTAsInVzZXJuYW1lIjoiZ2hfY2VyZWFsa2lsbCIsImVtYWlsIjoiZGVwcmF6ekBnbWFpbC5jb20iLCJjcmVhdGVkX2F0IjoiMjAxOC0wMi0xNVQxMDozMjozOC4wMTlaIiwiZmlyc3RfbmFtZSI6IlBhdWwiLCJsYXN0X25hbWUiOiJEZXByYXoiLCJjb21wYW55IjoiIiwiYWNjb3VudF90eXBlIjoicGVyc29uYWwiLCJqd3Rfc2VjcmV0IjoiNkpZWVBUUEpSTDVaQTZRM0ZUUkE2VU1OQ0w3QVFEVlIiLCJoYXNfZGlzYWJsZWRfbmV3c2xldHRlciI6ZmFsc2UsInNvY2lhbF9zZXJ2aWNlX2FjY291bnQiOlt7ImNyZWF0ZWRfYXQiOiIyMDE4LTAyLTE1VDEwOjMyOjM4LjAxOVoiLCJpZCI6MTE1MzcsImJlbG9uZ3NfdG9fX3VzZXIiOnsiX19kZWZlcnJlZCI6eyJ1cmkiOiIvcmVzaW4vdXNlcigzNDA1MCkifSwiX19pZCI6MzQwNTB9LCJwcm92aWRlciI6ImdpdGh1YiIsInJlbW90ZV9pZCI6IjI5MjM0MTMiLCJkaXNwbGF5X25hbWUiOiJjZXJlYWxraWxsIiwiX19tZXRhZGF0YSI6eyJ1cmkiOiIvcmVzaW4vc29jaWFsX3NlcnZpY2VfYWNjb3VudCgxMTUzNykiLCJ0eXBlIjoiIn19XSwiaGFzUGFzc3dvcmRTZXQiOmZhbHNlLCJuZWVkc1Bhc3N3b3JkUmVzZXQiOmZhbHNlLCJwdWJsaWNfa2V5Ijp0cnVlLCJmZWF0dXJlcyI6W10sImludGVyY29tVXNlck5hbWUiOiJnaF9jZXJlYWxraWxsIiwiaW50ZXJjb21Vc2VySGFzaCI6IjkwYWZiZTRkZThkNmU5MDBmYWJiMTIyMzU1MjE4ZWMyNTkyOWRhYTY1NDMyYzcwZjQ0OGRkZWNlZDQxNmVkN2IiLCJwZXJtaXNzaW9ucyI6W10sImF1dGhUaW1lIjoxNTIyOTMwMTM5NTgyLCJhY3RvciI6MjU2MTAwMSwiaWF0IjoxNTIzNjA4ODg2LCJleHAiOjE1MjQyMTM2ODZ9.dNZFqkvt8OY9oPyyW14nubn5j6jHBTEafsT4ku0JuL8'


def start_ewf_client():
    subprocess.Popen(["/usr/local/bin/ewf-client", "--jsonrpc-apis", "all", "--reserved-peers",
                      "/Users/r2d2/software/ewf/tobalaba-reserved-peers"], stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE)
    print('waiting for ewf-client...\n\n')
    time.sleep(60)


if __name__ == '__main__':
    configuration = core.print_config(JSON)
    config = {
        "prod_chain_file": PRODUCTION_CHAIN,
        "cons_chain_file": CONSUMPTION_CHAIN,
        "configuration": configuration
    }
    core.log(**config)
    # core.schedule(config)
