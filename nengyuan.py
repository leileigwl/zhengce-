import requests
from bs4 import BeautifulSoup
import time
import sys
import os
from datetime import datetime, timedelta

# 从文件中读取 Notion Database ID 和 API Token
def read_config(file_path):
    try:
        with open(file_path, "r") as prf:
            page_id = prf.readline().strip()
            token = prf.readline().strip()
        return page_id, token
    except FileNotFoundError:
        print(f"错误：找不到文件 {file_path}，请检查文件路径是否正确。")
        print("当前工作目录:", os.getcwd())  # 打印当前工作目录
        sys.exit(1)  # 退出程序

# 获取已录入的政策信息
def fetch_existing_policies(page_id, token):
    url = f"https://api.notion.com/v1/databases/{page_id}/query"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Notion-Version": "2022-06-28",
        "Authorization": "Bearer " + token
    }
    
    existing_policies = []
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        for result in data.get("results", []):
            title_property = result['properties']['标题']['title']
            # 检查标题是否存在且不为空
            if title_property and len(title_property) > 0:
                title = title_property[0]['text']['content']
                existing_policies.append(title)
    else:
        print("获取已录入政策信息失败，状态码:", response.status_code)

    return existing_policies

# 获取今天和昨天的日期
def get_today_and_yesterday():
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    return today, yesterday

# 爬取新能源网政策信息
def fetch_policy_info(page_id, token):
    url = "http://www.china-nengyuan.com/news/news_list_6.html"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # 获取已录入的政策信息
    existing_policies = fetch_existing_policies(page_id, token)

    # 爬取新的政策信息
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print("请求失败，状态码:", response.status_code)
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup.prettify())  # 打印爬取到的 HTML 内容，便于调试
    policies = []
    
    today, yesterday = get_today_and_yesterday()  # 获取今天和昨天的日期
    
    # 定义关键词
    keywords = {
        # 各省份
        "北京": "地方",
        "天津": "地方",
        "上海": "地方",
        "重庆": "地方",
        "河北": "地方",
        "山西": "地方",
        "内蒙古": "地方",
        "辽宁": "地方",
        "吉林": "地方",
        "黑龙江": "地方",
        "江苏": "地方",
        "浙江": "地方",
        "安徽": "地方",
        "福建": "地方",
        "江西": "地方",
        "山东": "地方",
        "河南": "地方",
        "湖北": "地方",
        "湖南": "地方",
        "广东": "地方",
        "广西": "地方",
        "海南": "地方",
        "四川": "地方",
        "贵州": "地方",
        "云南": "地方",
        "西藏": "地方",
        "陕西": "地方",
        "甘肃": "地方",
        "青海": "地方",
        "宁夏": "地方",
        "新疆": "地方",
        "香港": "地方",
        "澳门": "地方",
        "台湾": "地方",

        # 国外重点国家
        "美国": "地方",
        "德国": "地方",
        "法国": "地方",
        "英国": "地方",
        "日本": "地方",
        "韩国": "地方",
        "加拿大": "地方",
        "澳大利亚": "地方",
        "印度": "地方",
        "巴西": "地方",
        "新加坡": "地方",
        "瑞士": "地方",
        "挪威": "地方",
        "丹麦": "地方",
        "荷兰": "地方",
        "瑞典": "地方",
        "新西兰": "地方",
        "阿根廷": "地方",
        "南非": "地方",
        "俄罗斯": "地方",
        "意大利": "地方",

        # 新能源相关技术
        "光伏": "技术",
        "风能": "技术",
        "储能": "技术",
        "氢能": "技术",
        "电动车": "技术",
        "智能电网": "技术",
        "可再生能源": "技术",
        "碳捕集": "技术",
        "碳交易": "技术",
        "绿色建筑": "技术",
        "生物质能": "技术",
        "海洋能": "技术",
        "地热能": "技术",
        "智能交通": "技术",
        "节能技术": "技术",

        # 新能源和双碳领域的大公司
        "华为": "公司",
        "阳光电源": "公司",
        "隆基股份": "公司",
        "宁德时代": "公司",
        "比亚迪": "公司",
        "天合光能": "公司",
        "金风科技": "公司",
        "国电南瑞": "公司",
        "中兴能源": "公司",
        "中广核": "公司",
        "特斯拉": "公司",
        "西门子": "公司",
        "GE": "公司",
        "恩智浦半导体": "公司",
        "ABB": "公司",
        "施耐德电气": "公司",

        # 政策层级
        "国家级": "政策层级",
        "省级": "政策层级",
        "新能源汽车": "政策层级",
        "市级": "政策层级",
        "县级": "政策层级",
        "地方政府": "政策层级",
        "中央政府": "政策层级",
        "国际组织": "政策层级",
        "联合国": "政策层级",
        "世界银行": "政策层级",
        "国际能源署": "政策层级",

        # 其他关键词
        "双碳": "政策",
        "减排": "政策",
        "可持续发展": "政策",
        "绿色经济": "政策",
        "环保": "环境",
        "政策": "政策",
        "发展": "发展",
        "投资": "投资",
        "创新": "创新",
        "市场": "市场",
        "法规": "法规",
        "气候变化": "政策",
        "生态保护": "政策",
        "清洁能源": "政策",
        "环境治理": "政策",
    }

    # 查找所有政策信息行
    rows = soup.find_all('tr', class_='member_tr_row')
    for row in rows:
        title_tag = row.find('a')
        if title_tag:
            title = title_tag.text.strip()
            link = "http://www.china-nengyuan.com" + title_tag['href']  # 补充完整链接
            date = row.find_all('td')[-1].text.strip()  # 获取最后一个 <td> 中的日期

            # 提取关键词
            extracted_keywords = [keyword for keyword in keywords if keyword in title]

            # 仅录入今天和昨天的内容
            if date in (today, yesterday) and title not in existing_policies:
                policies.append({
                    '标题': title,
                    '链接': link,
                    '日期': date,
                    '关键词': ', '.join(extracted_keywords)  # 只保留关键词
                })

    return policies

# 将政策信息导入 Notion
def import_to_notion(policies, page_id, token):
    url = "https://api.notion.com/v1/pages"
    
    print("爬取到的政策信息:")
    for policy in policies:
        print(f"标题: {policy['标题']}, 链接: {policy['链接']}, 日期: {policy['日期']}, 关键词: {policy['关键词']}")

    for policy in policies:
        p = {
            "parent": {"database_id": page_id},
            "properties": {
                "标题": {"title": [{"type": "text", "text": {"content": policy['标题']}}]},
                "链接": {"url": policy['链接']},
                "日期": {"date": {"start": policy['日期']}},
                "关键词": {"multi_select": [{'name': keyword} for keyword in policy['关键词'].split(', ') if keyword]}  # 使用 multi_select 格式
            }
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        }

        r = requests.post(url, json=p, headers=headers)

        if r.status_code == 200:
            print(f"导入Notion成功: {policy['标题']}")
        else:
            print(f"导入Notion失败: {policy['标题']}, 状态码: {r.status_code}, 错误信息: {r.text}")

# 主函数
if __name__ == '__main__':
    page_id, token = read_config("config.txt")  # 假设配置文件名为 config.txt
    policies = fetch_policy_info(page_id, token)
    import_to_notion(policies, page_id, token)

    time.sleep(2)  # 延迟 2 秒