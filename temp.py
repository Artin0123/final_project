from flask import Flask, request, jsonify
import mysql.connector
import discord
from discord.ext import commands
import asyncio
import threading
from config import TOKEN  # 將你的 Discord Token 存在 config.py 中
import signal
import sys

# 創建 Flask 應用
app = Flask(__name__)

# conn = mysql.connector.connect(
#     user="G2", password="8D5s6Mxu", host="127.0.0.1", database="G2_example"
# )
# cursor = conn.cursor()

# 創建 Discord 客戶端
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


# Discord 事件處理
@bot.event
async def on_ready():
    print(f"{bot.user} 已經成功登入!")


@bot.event
async def on_message(message):
    # 避免機器人回覆自己的訊息
    if message.author == bot.user:
        return

    # 基本對話功能
    if message.content.lower() == "hello":
        await message.channel.send("Hi there!")
    elif message.content.lower() == "你好":
        await message.channel.send("你好啊！")

    # 處理命令
    await bot.process_commands(message)


# Discord 命令
@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"Pong! 延遲: {round(bot.latency * 1000)}ms")


@bot.command(name="echo")
async def echo(ctx, *, message):
    await ctx.send(message)


@bot.command(name="new")
async def get_latest(ctx):
    try:
        # 建立資料庫連線
        conn = mysql.connector.connect(
            user="G2", password="8D5s6Mxu", host="127.0.0.1", database="G2_example"
        )
        cursor = conn.cursor(dictionary=True)

        # 查詢最新一筆資料
        cursor.execute(
            "SELECT datetime, temp, moist FROM data ORDER BY datetime DESC LIMIT 1"
        )
        result = cursor.fetchone()

        if result:
            # 格式化回應訊息
            response = (
                f"最新資料：\n"
                f"時間：{result['datetime']}\n"
                f"溫度：{result['temp']}°C\n"
                f"濕度：{result['moist']}%"
            )
        else:
            response = "目前沒有任何資料"

        await ctx.send(response)

    except mysql.connector.Error as db_error:
        await ctx.send(f"資料庫錯誤：{str(db_error)}")

    except Exception as e:
        await ctx.send(f"發生未預期的錯誤：{str(e)}")

    finally:
        if "cursor" in locals():
            cursor.close()
        if "conn" in locals():
            conn.close()


# Flask 路由
@app.route("/")
def home():
    return "Discord Bot is running!"


# @app.route("/latest", methods=["POST", "GET"])
# def upload():
# if request.method == "POST":
#     try:
#         post_data = request.get_json()

#         if not post_data:
#             return jsonify({"status": 1, "message": "Missing JSON body!"}), 400

#         required_fields = ["datetime", "temp", "moist"]
#         for field in required_fields:
#             if field not in post_data or not post_data[field]:
#                 return (
#                     jsonify(
#                         {"status": 1, "message": f"Missing or empty field: {field}"}
#                     ),
#                     400,
#                 )

#         datetime = post_data["datetime"]
#         temp = post_data["temp"]
#         moist = post_data["moist"]

#         cursor = conn.cursor(buffered=True)
#         cursor.execute(
#             "INSERT INTO data (datetime, temp, moist) VALUES (%s, %s, %s)",
#             [datetime, temp, moist],
#         )
#         conn.commit()
#         return jsonify({"status": 0, "message": "Success!"})

#     except mysql.connector.Error as db_error:
#         return (
#             jsonify({"status": 2, "message": f"Database error: {str(db_error)}"}),
#             500,
#         )

#     except Exception as e:
#         return jsonify({"status": 3, "message": f"Unexpected error: {str(e)}"}), 500
# else:
#     try:
#         post_data = request.get_json()

#         if not post_data:
#             return jsonify({"status": 1, "message": "Missing JSON body!"}), 400

#         required_fields = ["datetime", "temp", "moist"]
#         for field in required_fields:
#             if field not in post_data or not post_data[field]:
#                 return (
#                     jsonify(
#                         {"status": 1, "message": f"Missing or empty field: {field}"}
#                     ),
#                     400,
#                 )

#         datetime = post_data["datetime"]
#         temp = post_data["temp"]
#         moist = post_data["moist"]

#         cursor = conn.cursor(buffered=True)
#         cursor.execute("SELECT * FROM data ORDER BY id DESC LIMIT 1")
#         conn.commit()
#         result = cursor.fetchall()
#         return jsonify({"status": 0, "data": result})

#     except mysql.connector.Error as db_error:
#         return (
#             jsonify({"status": 2, "message": f"Database error: {str(db_error)}"}),
#             500,
#         )

#     except Exception as e:
#         return jsonify({"status": 3, "message": f"Unexpected error: {str(e)}"}), 500


# 啟動 Discord Bot
def run_bot():
    bot.run(TOKEN)


def signal_handler(sig, frame):
    print("\n正在關閉服務...")
    # 關閉資料庫連線
    # cursor.close()
    # conn.close()
    # 關閉 Discord bot
    bot.close()
    sys.exit(0)


# 主程式
if __name__ == "__main__":
    # 註冊信號處理
    signal.signal(signal.SIGINT, signal_handler)

    # 在新的線程中運行 Discord bot
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    # 運行 Flask 應用
    app.run(host="0.0.0.0", port=5000)

    # app.run(port=30002)
