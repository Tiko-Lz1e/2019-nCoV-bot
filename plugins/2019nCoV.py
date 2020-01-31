import datetime
import nonebot
import requests
import json
import os
import pytz
from nonebot import on_command, CommandSession
from bs4 import BeautifulSoup


provinces = ['河北', '山西', '黑龙江', '吉林', '辽宁省', '陕西', '甘肃', '青海', '山东', '河南', '江苏', '浙江', '安徽', '江西',
             '福建', '台湾', '湖北', '湖南', '广东', '海南', '四川', '云南', '贵州', '香港', '澳门', '北京', '上海', '重庆',
             '深圳', '新疆', '西藏', '宁夏', '内蒙古', '广西']


@on_command('疫情', shell_like=True)  # 命令处理
async def nCoV(session):
    area = session.get('area')  # 获取命令参数
    result = await get_tencent_result(area)  # 全部数据来自腾讯网

    if result:
        formated_result = await format_result_tencent(result)
    else:
        formated_result = "未查询到%s的信息" % area
    if formated_result:
        await session.send(formated_result)


@nCoV.args_parser  # 命令参数处理
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()

    if stripped_arg:
        session.state['area'] = stripped_arg
    else:
        session.state['area'] = '全国'


async def get_tencent_result(area):
    result = None
    url = 'https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5'
    r = requests.get(url).text
    r_json = json.loads(json.loads(r)['data'])

    if area and area in ['全国', '中国', 'china']:
        result = r_json['chinaTotal']
        result['area'] = '全国'
        result['confirm_adds'] = int(result['confirm']) - int(r_json['chinaDayList'][-1]['confirm'])
    else:
        # 其他国家数据
        for i in range(1, len(r_json['areaTree'])):
            if area == r_json['areaTree'][i]['name']:
                result = r_json['areaTree'][i]['total']
                result['area'] = area
                result['confirm_adds'] = r_json['areaTree'][i]['today']['confirm']

        if not result:
            # 省级数据
            r_tree = r_json['areaTree'][0]['children']
            for detail_pro in r_tree:
                if area == detail_pro['name']:
                    result = detail_pro['total']
                    result['area'] = area
                    result['confirm_adds'] = detail_pro['today']['confirm']
                else:
                    # 城市数据
                    for detail_city in detail_pro['children']:
                        if area == detail_city['name']:
                            result = detail_city['total']
                            result['area'] = area
                            result['confirm_adds'] = detail_city['today']['confirm']

    return result


async def format_result_tencent(result):
    """
        将字典处理成字符串
        :param result: 包含数据的字典
        :return: 发送给用户的字符串
    """
    format_string = ''
    try:
        format_string += ' %s' % result['area']
    except KeyError or TypeError:
        pass
    finally:
        format_string += ' \n\t确诊%d例（%s）' % (int(result['confirm']),
                                             result['confirm_adds'] if result['confirm_adds'] < 0 else '+' + str(result['confirm_adds']))
        if result['area'] in ['全国']:
            format_string += '\n\t疑似%d例' % int(result['suspect'])
        format_string += '\n\t治愈%d例 \n\t死亡%d例\n\n（数据来自腾讯网）' % (
             int(result['heal']),
             int(result['dead']))

    return format_string


