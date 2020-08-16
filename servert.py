from flask import Flask,request,abort
# from flask import request
import requests
import hashlib
import xmltodict
import time
from AccessToken import accessToken
import json

# res=requests.get('https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=wx860ac5bac6a3b1b3&secret=4426e4e9ab960834ba91ac0f4ec12d52')
# print(res.text)
# import ssl
# ssl._create_default_https_context = ssl._create_unverified_context
app=Flask(__name__)
@app.route('/wxc',methods = ['GET','POST'])
@app.route('/wx/',methods = ['GET','POST'])
def handle():
        signature = request.args.get('signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')

        if(not all([signature,timestamp,nonce])):
            abort(400)
        token='sunlin0903'
        list = [timestamp,token, nonce]
        list.sort()
        sha1 = hashlib.sha1()
        sha1.update("".join(list).encode('utf-8'))
        hashcode = sha1.hexdigest()
        access_token=accessToken.get_access_token()
        print('access_token',access_token)
        print("handle/GET func: hashcode, signature: ", hashcode, signature)

        if request.method == 'GET':
            echostr = request.args.get('echostr')
            if hashcode == signature:
                return echostr
            else:
                return abort(400)
        elif request.method == 'POST':
            webData = request.data
            xml_dict=xmltodict.parse(webData)
            xml_dict=xml_dict.get('xml')
            touser=xml_dict['FromUserName']
            fromuser=xml_dict['ToUserName']
            creat_time=int(time.time())

            msg_type = xml_dict['MsgType']
            if(msg_type=='text'):
                content = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx860ac5bac6a3b1b3&redirect_uri=62.234.124.201%2Fwx%2Fweb&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect'
                back_dict = {
                    'xml': {
                        'ToUserName': touser,
                        'FromUserName': fromuser,
                        'CreateTime': creat_time,
                        'Content': content,
                        'MsgType': msg_type
                    }
                }
            elif(msg_type=='image'):
                media_id=xml_dict['MediaId']
                back_dict = {
                    'xml': {
                        'ToUserName': touser,
                        'FromUserName': fromuser,
                        'CreateTime': creat_time,
                        'Image': {
                            'MediaId': media_id
                        },
                        'MsgType': msg_type
                    }
                }
            back_dict=xmltodict.unparse(back_dict)
            return back_dict

        # 后台打日志
        # recMsg = receive.parse_xml(webData)
        # if isinstance(recMsg, receive.Msg) and recMsg.MsgType == 'text':
        #     toUser = recMsg.FromUserName
        #     fromUser = recMsg.ToUserName
        #     content = "test"
        #     replyMsg = reply.TextMsg(toUser, fromUser, content)
        #     return replyMsg.send()
        # else:
        #     print
        #     "暂且不处理"
        #     return "success"
@app.route('/wxc',method=['GET','POST'])
def wxcHandle():

if __name__=='__main__':
    app.run(host="0.0.0.0", port=3000,debug=True)
@app.route('/wx/web',methods = ['GET'])
def indexHandle():
    code = request.args.get('code')
    print(code)
    return ''
