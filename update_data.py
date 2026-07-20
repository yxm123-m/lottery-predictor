"""
彩票数据自动更新脚本
从官方网站抓取最新开奖数据并更新 lottery_logic.py
"""

import urllib.request
import json
import re
import os
from datetime import datetime


def fetch_dlt_data(count=100):
    """获取大乐透数据（从500彩票网）"""
    url = f"https://datachart.500.com/dlt/history/newinc/history.php?start=26001&end=26200"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as response:
        html = response.read().decode('utf-8', errors='ignore')

    tbody_match = re.search(r'<tbody[^>]*>(.*?)</tbody>', html, re.DOTALL)
    if not tbody_match:
        return []

    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', tbody_match.group(1), re.DOTALL)

    dlt_data = []
    for row in rows:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        if len(cells) >= 9:
            cell_text = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
            issue = cell_text[1]
            if issue.startswith('26'):
                front = sorted([int(cell_text[2]), int(cell_text[3]), int(cell_text[4]), int(cell_text[5]), int(cell_text[6])])
                back = sorted([int(cell_text[7]), int(cell_text[8])])
                dlt_data.append({
                    'issue': issue[-3:],
                    'front': front,
                    'back': back
                })

    return dlt_data


def fetch_ssq_data(count=100):
    """获取双色球数据（从中国福彩官网）"""
    url = f"https://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice?name=ssq&issueCount={count}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as response:
        data = json.loads(response.read().decode('utf-8'))

    ssq_data = []
    for item in data['result']:
        if item['code'].startswith('2026'):
            red = [int(x) for x in item['red'].split(',')]
            blue = int(item['blue'])
            issue = item['code'][-3:]
            ssq_data.append({
                'issue': issue,
                'front': sorted(red),
                'back': [blue]
            })

    return ssq_data


def generate_data_code(lottery_type, data):
    """生成Python数据代码"""
    lines = [f'        # 2026年真实开奖数据（更新于 {datetime.now().strftime("%Y-%m-%d")}）']
    for d in data:
        lines.append(f'        {{"issue": "{d["issue"]}", "front": {d["front"]}, "back": {d["back"]}}},')
    return '\n'.join(lines)


def update_lottery_logic(dlt_data, ssq_data):
    """更新 lottery_logic.py 文件"""
    file_path = os.path.join(os.path.dirname(__file__), 'lottery_logic.py')

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 更新大乐透数据
    dlt_start = content.find('    "大乐透": [')
    dlt_end = content.find('    ],', dlt_start) + 4
    new_dlt = f'    "大乐透": [\n{generate_data_code("大乐透", dlt_data)}\n    ],'
    content = content[:dlt_start] + new_dlt + content[dlt_end:]

    # 更新双色球数据
    ssq_start = content.find('    "双色球": [')
    ssq_end = content.find('    ],', ssq_start) + 4
    new_ssq = f'    "双色球": [\n{generate_data_code("双色球", ssq_data)}\n    ],'
    content = content[:ssq_start] + new_ssq + content[ssq_end:]

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return True


def push_to_github():
    """推送到GitHub"""
    import base64
    import urllib.request

    # 获取 GitHub token
    token = os.popen('gh auth token').read().strip()
    repo = 'yxm123-m/lottery-predictor'
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'lottery-predictor-updater'
    }

    def api_call(endpoint, method='GET', data=None):
        url = f'https://api.github.com/repos/{repo}/{endpoint}'
        req_data = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())

    # 读取文件
    file_path = os.path.join(os.path.dirname(__file__), 'lottery_logic.py')
    with open(file_path, 'rb') as f:
        content = base64.b64encode(f.read()).decode()

    # 获取当前状态
    ref = api_call('git/refs/heads/master')
    parent_sha = ref['object']['sha']
    commit = api_call(f'git/commits/{parent_sha}')
    tree_sha = commit['tree']['sha']

    # 创建 blob
    blob = api_call('git/blobs', 'POST', {'encoding': 'base64', 'content': content})
    blob_sha = blob['sha']

    # 创建 tree
    tree_data = {
        "base_tree": tree_sha,
        "tree": [{"path": "lottery_logic.py", "mode": "100644", "type": "blob", "sha": blob_sha}]
    }
    new_tree = api_call('git/trees', 'POST', tree_data)

    # 创建 commit
    today = datetime.now().strftime("%Y-%m-%d")
    commit_data = {
        "message": f"data: 更新开奖数据至 {today}",
        "tree": new_tree['sha'],
        "parents": [parent_sha]
    }
    new_commit = api_call('git/commits', 'POST', commit_data)

    # 更新 ref
    ref_data = {"sha": new_commit['sha'], "force": True}
    req = urllib.request.Request(
        f'https://api.github.com/repos/{repo}/git/refs/heads/master',
        data=json.dumps(ref_data).encode(),
        headers=headers,
        method='PATCH'
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return True


def main():
    """主函数"""
    print(f"[TIME] 开始更新彩票数据 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # 获取数据
        print("[FETCH] 正在获取大乐透数据...")
        dlt_data = fetch_dlt_data()
        print(f"   获取到 {len(dlt_data)} 期数据")

        print("[FETCH] 正在获取双色球数据...")
        ssq_data = fetch_ssq_data()
        print(f"   获取到 {len(ssq_data)} 期数据")

        if not dlt_data or not ssq_data:
            print("[ERROR] 获取数据失败")
            return False

        # 更新本地文件
        print("[UPDATE] 正在更新本地文件...")
        update_lottery_logic(dlt_data, ssq_data)
        print("   本地文件更新完成")

        # 推送到GitHub
        print("[PUSH] 正在推送到GitHub...")
        push_to_github()
        print("   GitHub推送成功")

        print(f"[OK] 更新完成！大乐透: {len(dlt_data)}期, 双色球: {len(ssq_data)}期")
        return True

    except Exception as e:
        print(f"[ERROR] 更新失败: {e}")
        return False


if __name__ == '__main__':
    main()
