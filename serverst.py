from flask import Flask, request, abort
# from flask import request
import requests
import hashlib
import xmltodict
import time
from AccessToken import accessToken
from spider import Spider
import json

config_json = {
    'gdkey': '0b85143140e5c8323b9e8b6cd5500087'
}
app = Flask(__name__)

robot=Spider()
@app.route('/wxc', methods=['GET', 'POST'])
def handle():
    signature = request.args.get('signature')
    timestamp = request.args.get('timestamp')
    nonce = request.args.get('nonce')

    if (not all([signature, timestamp, nonce])):
        return abort(400)
    token = 'sunlin0903'
    list = [timestamp, token, nonce]
    list.sort()
    sha1 = hashlib.sha1()
    sha1.update("".join(list).encode('utf-8'))
    hashcode = sha1.hexdigest()
    access_token = accessToken.get_access_token()
    print('access_token', access_token)
    print("handle/GET func: hashcode, signature: ", hashcode, signature)

    if request.method == 'GET':
        echostr = request.args.get('echostr')
        if hashcode == signature:
            return echostr
        else:
            return abort(400)
    elif request.method == 'POST':
        webData = request.data
        xml_dict = xmltodict.parse(webData)
        xml_dict = xml_dict.get('xml')
        touser = xml_dict['FromUserName']
        fromuser = xml_dict['ToUserName']
        creat_time = int(time.time())

        msg_type = xml_dict['MsgType']
        if (msg_type == 'text'):
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
        elif (msg_type == 'image'):
            media_id = xml_dict['MediaId']
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
        back_dict = xmltodict.unparse(back_dict)
        return back_dict


@app.route('/wxc/api/', methods=['GET', 'POST'])
def wxc_api_handle():
    pos = request.args.get('pos')
    robot.setPos(pos.split(',')[1],pos.split(',')[0])
    with requests.get('https://restapi.amap.com/v3/assistant/coordinate/convert', params={
        'key': config_json['gdkey'],
        'locations': pos,
        'coordsys': 'gps'
    }) as res:
        resdata = json.loads(res.text)
        if (resdata['infocode'] == '10000'):
            with requests.get('https://restapi.amap.com/v3/geocode/regeo', params={'key': config_json['gdkey'], 'location': resdata['locations']}) as repores:
                repores_data=json.loads(repores.text)
                if(repores_data['regeocode']['addressComponent']['city']=='' or len(repores_data['regeocode']['addressComponent']['city'])==0):
                  citypo=repores_data['regeocode']['addressComponent']['province']
                else:
                  citypo = repores_data['regeocode']['addressComponent']['city']
                chartData=robot.getHtmlCodeByCity(repores_data['regeocode']['addressComponent']['district'].replace('区','').replace('县',''),[repores_data['regeocode']['addressComponent']['district'],citypo,repores_data['regeocode']['addressComponent']['province']])
                with requests.get('https://restapi.amap.com/v3/weather/weatherInfo', params={'key':config_json['gdkey'], 'city': repores_data['regeocode']['addressComponent']['adcode'],'extensions':'base'}) as weatherres:
                    with requests.get('https://restapi.amap.com/v3/weather/weatherInfo', params={'key':config_json['gdkey'], 'city': repores_data['regeocode']['addressComponent']['adcode'],'extensions':'all'}) as weatherallres:

                        weatherres_data = json.loads(weatherres.text)
                        weatherallres_data=json.loads(weatherallres.text)
                        weatherres_data['forecasts']=weatherallres_data['forecasts']
                        weatherres_data['weatherres_data']=chartData
                        if(weatherres_data['infocode'] == '10000'):
                            return json.dumps(weatherres_data)
                        else:
                            return 'errorCode:'+weatherres_data['infocode']

            return 'test'
        else:
            return 'error'

@app.route('/wxc/api/news', methods=['GET'])
def wxc_api_getnews():
    print(8888888888888888888888)
    return robot.getNewsDataByCode()
@app.route('/wxc/api/getdayinfo', methods=['GET'])
def get_day_info():
  def getLifeInfo(self):
    return robot.getLifeInfo()
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3001, debug=True,ssl_context=('/home/yuxingyang/1_www.yxy311.cn_bundle.pem', '/etc/nginx/2_www.yxy311.cn.key'))


@app.route('/wxc/web', methods=['GET'])
def indexHandle():
    code = request.args.get('code')
    print(code)
    return ''
