import pandas as pd
import uuid
import random
from datetime import datetime, timedelta

# パラメータ設定
start_time = datetime(2025, 1, 29, 0, 0, 0)  # 開始時刻
N = 3  # 出力するUUIDの数
uuids = [str(uuid.uuid4()) for _ in range(N)]  # N個のUUIDを生成
max_x, max_y = 600, 600  # 座標の最大値
num_records = 500  # レコードの数

# 各UUIDの初期座標を設定
initial_positions = {uuid: (random.randint(0, max_x), random.randint(0, max_y)) for uuid in uuids}
current_positions = initial_positions.copy()
data = []

# レコードを生成
i = 0
while i < num_records:
    timestamp = start_time + timedelta(seconds=i)  # 時刻を1秒ずつ追加
    num_uuids = random.randint(1, N)  # 同時刻に出力するUUIDの個数をランダムに決定
    chosen_uuids = random.sample(uuids, num_uuids)  # ランダムに選択されたUUID

    for person_id in chosen_uuids:
        current_x, current_y = current_positions[person_id]
        data.append([timestamp.isoformat(), person_id, current_x, current_y])
        
        # 次の座標をランダムに生成
        next_x = min(max(current_x + random.randint(-10, 10), 0), max_x)
        next_y = min(max(current_y + random.randint(-10, 10), 0), max_y)
        current_positions[person_id] = (next_x, next_y)
    
    i += 1

# データフレームを作成
df = pd.DataFrame(data, columns=['timestamp', 'person_id', 'x', 'y'])

# CSVとして出力
df.to_csv('data.csv', index=False)
print("CSVファイル 'data.csv' が生成されました。")

