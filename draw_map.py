import pandas as pd
import cv2
import matplotlib.pyplot as plt
from datetime import datetime

# 描画方法を設定 (Trueなら軌跡、Falseなら丸)
draw_trajectory = False

# 事前に定義した10個のカスタムカラー（BGR形式）
colors = [
    (0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255),
    (0, 255, 255), (128, 0, 128), (128, 128, 0), (0, 128, 128), (128, 0, 0)
]
timestamp_color = (0, 255, 0)  # 緑色 (タイムスタンプの色)

# CSVファイルの読み込み
data = pd.read_csv('data.csv')

# マップ画像・最大幅・最大高さの設定
map_image = cv2.imread('map.jpg')
map_width, map_height = map_image.shape[1], map_image.shape[0]

# 最大幅・最大高さを設定
max_x, max_y = 600, 600  # 例として最大値を設定

# 座標をマップの解像度に合わせてスケーリング
data['scaled_x'] = (data['x'] / max_x) * map_width
data['scaled_y'] = (data['y'] / max_y) * map_height

# 人物ごとに時系列でデータを分ける
data['timestamp'] = pd.to_datetime(data['timestamp'])
data.sort_values(by=['person_id', 'timestamp'], inplace=True)

# 各人物に色を割り振る
unique_person_ids = data['person_id'].unique()
person_color_map = {person_id: colors[i % len(colors)] for i, person_id in enumerate(unique_person_ids)}

# 映像作成の設定
output_video_path = 'output_with_timestamp.avi'
height, width, _ = map_image.shape

# 比率の定義 （例: 映像の1秒が実際の10秒に対応）
time_ratio = 10

# フレームレートの設定
fps = 10
total_frames = int(len(data['timestamp'].unique()) * (1 / time_ratio) * fps)

out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'DIVX'), fps, (width, height))

# 映像の生成
for frame_idx in range(total_frames):
    frame_time = data['timestamp'].min() + pd.Timedelta(seconds=frame_idx * time_ratio / fps)
    frame = map_image.copy()
    for person_id in data['person_id'].unique():
        person_data = data[(data['person_id'] == person_id) & (data['timestamp'] <= frame_time)]
        color = person_color_map.get(person_id, (0, 255, 255))  # 定義した色を割り振る

        if draw_trajectory:
            # 軌跡を描画
            for i in range(len(person_data) - 1):
                start_point = (int(person_data.iloc[i]['scaled_x']), int(person_data.iloc[i]['scaled_y']))
                end_point = (int(person_data.iloc[i + 1]['scaled_x']), int(person_data.iloc[i + 1]['scaled_y']))
                cv2.line(frame, start_point, end_point, color, 2)  # カスタムカラーで軌跡を描画

            # シーンの最後の位置にperson_idと座標を表示
            if not person_data.empty:
                last_position = (int(person_data.iloc[-1]['scaled_x']), int(person_data.iloc[-1]['scaled_y']))
                cv2.putText(frame, person_id, (last_position[0] + 5, last_position[1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1, cv2.LINE_AA)
                cv2.putText(frame, f"({last_position[0]}, {last_position[1]})", (last_position[0] + 5, last_position[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1, cv2.LINE_AA)
        else:
            # 現在位置を丸で描画
            if not person_data.empty:
                current_position = (int(person_data.iloc[-1]['scaled_x']), int(person_data.iloc[-1]['scaled_y']))
                cv2.circle(frame, current_position, 5, color, -1)  # カスタムカラーで現在位置を描画
                cv2.putText(frame, person_id, (current_position[0] + 5, current_position[1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1, cv2.LINE_AA)
                cv2.putText(frame, f"({current_position[0]}, {current_position[1]})", (current_position[0] + 5, current_position[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1, cv2.LINE_AA)

    # タイムスタンプの追加
    timestamp_str = frame_time.strftime('%Y-%m-%d %H:%M:%S')
    cv2.putText(frame, timestamp_str, (width - 250, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, timestamp_color, 1, cv2.LINE_AA)

    out.write(frame)

out.release()
print(f"動画が {output_video_path} に保存されました。")
