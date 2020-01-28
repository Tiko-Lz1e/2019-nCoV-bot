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
        if area in ['全国', '中国']:
            formated_result = await format_result_tencent_cn(result)
        else:
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
    url = 'https://view.inews.qq.com/g2/getOnsInfo?name='
    if area and area not in ['全国', '中国']:
        url += 'wuwei_ww_area_counts'
        r_detail = json.loads(json.loads(requests.get(url).text)['data'])

        # 处理省级数据，将省内各市数据加和
        if area in provinces:
            result = dict(country='中国', area=area, city='', confirm=0, suspect=0, dead=0, heal=0)
            for detail in r_detail:
                if detail['area'] == area:
                    result['confirm'] += detail['confirm']
                    result['dead'] += detail['dead']
                    result['heal'] += detail['heal']
        for detail in r_detail:
            if area in [detail['country'], detail['city']]:
                result = detail

    else:
        url += 'wuwei_ww_global_vars'
        r = requests.get(url)
        result = json.loads(json.loads(r.text)['data'])[0]

    return result


async def format_result_tencent(result):
    """
        将字典处理成字符串
        :param result: 包含数据的字典
        :return: 发送给用户的字符串
    """
    format_string = ''
    try:
        format_string += '%s' % result['country']
        format_string += ' %s' % result['area']
        format_string += ' %s' % result['city']
    except KeyError:
        pass
    finally:
        format_string += ' 确诊%d例 治愈%d例 死亡%d例\n\n（数据来自腾讯网）' % (
             result['confirm'], result['heal'], result['dead'])

    return format_string


async def format_result_tencent_cn(result):
    """
    将字典处理成字符串
    :param result: 包含数据的字典
    :return: 发送给用户的字符串
    """
    f_his = json.load(open('./TikoBot_QQ/plugins/his.json', 'r'))
    yestoday = str((datetime.datetime.today() + datetime.timedelta(-1)).strftime('%m.%d'))
    his = {'date': yestoday, 'confirm': '0', 'suspect': '0', 'dead': '0', 'heal': '0'}
    for i in f_his:
        if i['date'] == yestoday:
            his = i

    up_confirm = result['confirmCount'] - int(his['confirm'])
    up_suspect = result['suspectCount'] - int(his['suspect'])
    up_dead = result['deadCount'] - int(his['dead'])
    up_heal = result['cure'] - int(his['heal'])
    up = dict(up_confirm='+' + str(up_confirm) if up_confirm >= 0 else str(up_confirm),
              up_suspect='+' + str(up_suspect) if up_suspect >= 0 else str(up_suspect),
              up_dead='+' + str(up_dead) if up_dead >= 0 else str(up_dead),
              up_heal='+' + str(up_heal) if up_heal >= 0 else str(up_heal),
              )

    format_string = ''
    format_string += '全国\n\t确诊%d例（%s）\n\t疑似%d例（%s）\n\t治愈%d例（%s）\n\t死亡%d例（%s）' % (
        result['confirmCount'], up['up_confirm'], result['suspectCount'], up['up_suspect'],
        result['cure'], up['up_heal'], result['deadCount'], up['up_dead'])

    return format_string


@nonebot.scheduler.scheduled_job('cron', hour='*')
async def _():
    """
    北京时间0点自动更新全国记录文件
    :return:
    """
    now = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
    if now.hour == 0:
        with open('./TikoBot_QQ/plugins/his.json', 'w') as f:
            url = 'https://view.inews.qq.com/g2/getOnsInfo?name=wuwei_ww_cn_day_counts'
            r = requests.get(url)
            r_json = json.loads(r.text)['data']
            f.write(r_json)

