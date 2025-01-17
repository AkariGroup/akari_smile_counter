from depthai_sdk import OakCamera, TextPosition, Visualizer
from depthai_sdk.classes.packets import TwoStagePacket
import numpy as np
import cv2
import json
import time

# M5Stack表示関連のモジュール（M5Stackを使っている場合のみ）
from akari_client import AkariClient
from akari_client.color import Colors
from akari_client.position import Positions

akari = AkariClient()
m5 = akari.m5stack

# 関節制御用のインスタンスを取得する。
joints = akari.joints

# サーボONにする。
joints.enable_all_servo()


emotions = ['neutral', 'happy', 'sad', 'surprise', 'anger']

# Happyカウント用変数
happy_count = 0

# 最後に認識された感情を保持する変数
last_emotion = None

# jsonファイルのパス
json_path = "log/log.json"

# いいね数を表示する関数（M5Stackを使用する場合）


def display_happy_count(count):
    m5.set_display_text(
        text=f"Happy Count: {count}",
        pos_x=Positions.CENTER,
        pos_y=Positions.CENTER,
        size=3,
        text_color=Colors.RED,
        back_color=Colors.WHITE,
        refresh=True,
    )

# ログの読み込み


def load_happy_count():
    try:
        with open(json_path, 'r') as f:
            log = json.load(f)
        return log.get("happy_count", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

# ログの保存


def save_happy_count(count):
    with open(json_path, 'w') as f:
        json.dump({"happy_count": count}, f)

# カウントのリセット


def reset_happy_count():
    global happy_count
    happy_count = 0
    display_happy_count(happy_count)  # M5Stackに表示
    save_happy_count(happy_count)     # jsonに保存
    print("Happy count has been reset.")


# カウントの読み込み
happy_count = load_happy_count()

with OakCamera() as oak:
    color = oak.create_camera('color')
    det_nn = oak.create_nn('face-detection-retail-0004', color)
    det_nn.config_nn(resize_mode='crop')

    emotion_nn = oak.create_nn(
        'emotions-recognition-retail-0003', input=det_nn)

    def cb(packet: TwoStagePacket):
        global happy_count, last_emotion
        vis: Visualizer = packet.visualizer
        for det, rec in zip(packet.detections, packet.nnData):
            emotion_results = np.array(rec.getFirstLayerFp16())
            emotion_name = emotions[np.argmax(emotion_results)]

            # 'happy' が認識され、前回とは異なる感情の場合にカウントを増やす
            if emotion_name == 'happy' and last_emotion != 'happy':
                happy_count += 1
                print(f"Happy count: {happy_count}")
                display_happy_count(happy_count)  # M5Stackに表示
                save_happy_count(happy_count)     # カウントを保存
                # m5のデータを取得
                m5_data = m5.get()
                # ライトを点灯
                m5.set_dout(pin_id=0, value=True)
                m5.set_dout(pin_id=1, value=True)

                # 一回うなずく
                joints.set_joint_velocities(pan=9, tilt=9)
                joints.move_joint_positions(pan=0, tilt=0.25, sync=True)
                joints.move_joint_positions(tilt=-0.25, sync=True)
                joints.move_joint_positions(tilt=0.25, sync=True)

                # ライトを消す
                m5.set_dout(pin_id=0, value=False)
                m5.set_dout(pin_id=1, value=False)

            # 認識された感情を last_emotion に保存
            last_emotion = emotion_name

            vis.add_text(emotion_name,
                         bbox=(*det.top_left, *det.bottom_right),
                         position=TextPosition.BOTTOM_RIGHT)

        vis.draw(packet.frame)
        cv2.imshow(packet.name, packet.frame)

        # 'r' キーが押されたらカウントをリセット
        if cv2.waitKey(1) & 0xFF == ord('r'):
            reset_happy_count()

    oak.visualize(emotion_nn, callback=cb, fps=True)
    oak.visualize(det_nn.out.passthrough)
    oak.start(blocking=True)
