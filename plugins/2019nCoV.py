import requests
import json
from nonebot import on_command, CommandSession
from bs4 import BeautifulSoup


@on_command('疫情', shell_like=True)  # 命令处理
async def nCoV(session):
    area = session.get('area')  # 获取命令参数

    if area in ['全国', '中国']:
        result = await get_tencent_result(area)  # 国家级数据来自腾讯新闻
    else:
        result = await get_dxy_result(area)  # 省市级数据来自丁香园

    if result:
        if area in ['全国', '中国']:
            formated_result = await format_result_tencent(result)
        elif area in ['法国']:
            formated_result = await format_area_result_tencent(result)  # 外国数据
        else:
            formated_result = await format_result_dxy(result)
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
    """
    通过腾讯新闻api获取area地区数据
    :param area: 地区名
    :return: none或包含数据的字典
    """
    result = None
    url = 'https://view.inews.qq.com/g2/getOnsInfo?name='
    if area and area not in ['全国', '中国']:
        url += 'wuwei_ww_area_datas'
        r_detail = json.loads(json.loads(requests.get(url).text)['data'])

        for detail in r_detail:
            if area in [detail['country'], detail['area']]:
                result = detail

    else:
        url += 'wuwei_ww_global_vars'
        r = requests.get(url)
        result = json.loads(json.loads(r.text)['data'])[0]

    return result


async def get_dxy_result(area):
    """
    从丁香园html页面中获取数据
    :param area: 地区名
    :return: 包含数据的字典或者None
    """
    result = None
    url = 'https://3g.dxy.cn/newh5/view/pneumonia?enterid=1579582238'
    r = requests.get(url)
    r_bs = BeautifulSoup(str(r.content, 'utf-8'), 'html5lib')
    r_area = BeautifulSoup(str(r_bs.find(id='getAreaStat')), 'html5lib')
    r_area_text = r_area.get_text()[r_area.get_text().find('['):r_area.get_text().rfind(']')+1]

    r_area_json = json.loads(r_area_text)
    for detail in r_area_json:
        if area in [detail['provinceName'], detail['provinceShortName']]:
            result = detail
        elif area in [x['cityName'] for x in detail['cities']]:
            print(area)
            for i in range(len(detail['cities'])):
                city_detail = detail['cities'][i]
                if area == city_detail['cityName']:
                    city_detail['provinceName'] = detail['provinceName']
                    result = city_detail
    return result


async def format_result_tencent(result):
    """
    将字典处理成字符串
    :param result: 包含数据的字典
    :return: 发送给用户的字符串
    """
    format_string = ''
    format_string += '全国 确诊%d例 疑似%d例 治愈%d例 死亡%d例' % (
        result['confirmCount'], result['suspectCount'], result['cure'], result['deadCount'])

    return format_string


async def format_area_result_tencent(result):
    """
        将字典处理成字符串
        :param result: 包含数据的字典
        :return: 发送给用户的字符串
    """
    format_string = ''
    if result['country']:
        format_string += '%s' % result['country']
    if result['area']:
        format_string += ' %s' % result['area']
    if result['confirm'] and result['confirm'] > 0:
        format_string += ' 确诊%d例' % result['confirm']
    if result['suspect'] and result['suspect'] > 0:
        format_string += ' 疑似%d例' % result['suspect']
    if result['heal'] and result['heal'] > 0:
        format_string += ' 治愈%d例' % result['heal']
    if result['dead'] and result['dead'] > 0:
        format_string += ' 死亡%d例' % result['dead']

    return format_string


async def format_result_dxy(result):
    """
        将字典处理成字符串
        :param result: 包含数据的字典
        :return: 发送给用户的字符串
    """
    format_string = ''
    format_string += '%s' % result['provinceName']
    try:
        format_string += ' %s' % result['cityName']
    except KeyError:
        pass
    finally:
        format_string += ' 确诊%d例 疑似%d例 治愈%d例 死亡%d例\n\n（省市级数据来自丁香园）' % (
             result['confirmedCount'], result['suspectedCount'], result['curedCount'], result['deadCount'])

    return format_string
