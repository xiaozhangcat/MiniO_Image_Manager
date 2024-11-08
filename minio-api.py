from flask import Flask, jsonify, send_file, render_template, request, url_for, session
from minio import Minio
from minio.error import S3Error
from flask_httpauth import HTTPBasicAuth
import io

from werkzeug.utils import redirect

app = Flask(__name__)
app.secret_key = 'you_secret_key'

# MinIO 配置
MINIO_URL = 'your'
ACCESS_KEY = 'your'
SECRET_KEY = 'your'

# 创建 MinIO 客户端
client = Minio(MINIO_URL, access_key=ACCESS_KEY, secret_key=SECRET_KEY, secure=False)

bucket_name = None

auth = HTTPBasicAuth()

users = {
    "CuiCui": "CuiCui"
}

@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username
    return None

@app.route('/')
def home():
    return render_template('login.html')  # 进入 login.html 页面

@app.route('/login', methods=['POST'])
def login():
    data = request.json  # 从请求体获得 JSON 数据
    username = data.get('username')
    password = data.get('password')

    if verify_password(username, password):
        session['user'] = username
        return jsonify({"message": "Login successful"}), 200  # 登录成功
    else:
        return jsonify({"message": "Invalid username or password"}), 401  # 登录失败

@app.route('/index')
def index():
    if 'user' not in session:
        return redirect(url_for('home'))
    return render_template('index.html')  # 返回 index.html 页面


@app.route('/set_bucket', methods=['POST'])
def set_bucket():
    if 'user' not in session:  # 检查用户是否已登录
        return jsonify({"error": "Unauthorized access. Please log in."}), 401
    data = request.get_json()
    bucket_name = data.get('bucket_name')  # 获取从前端发送的 BUCKET_NAME
    if not bucket_name:
        return jsonify({"error": "Bucket name is required."}), 400
    session['bucket_name'] = bucket_name
    return jsonify({"message": f"Bucket name set to {bucket_name}"}), 200

@app.route('/api/images', methods=['GET'])
def list_images():
    if 'user' not in session:  # 检查用户是否已登录
        return jsonify({"error": "Unauthorized access. Please log in."}), 401

    if 'bucket_name' not in session:
        return jsonify({"error": "No bucket name set"}), 400
    try:
        images = []
        objects = client.list_objects(session['bucket_name'], recursive=True)
        for obj in objects:
            if obj.object_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                images.append(obj.object_name)

        return jsonify(images)
    except S3Error as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/image/<string:image_name>', methods=['GET'])
def get_image(image_name):
    if 'user' not in session:  # 检查用户是否已登录
        return jsonify({"error": "Unauthorized access. Please log in."}), 401

    if 'bucket_name' not in session:
        return jsonify({"error": "No bucket name set"}), 400

    try:
        response = client.get_object(session['bucket_name'], image_name)
        return send_file(io.BytesIO(response.read()), mimetype='image/jpeg')
    except S3Error as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/image/rename/<string:old_image_name>/<string:new_image_name>', methods=['PUT'])
@auth.login_required()
def rename_image(old_image_name, new_image_name):
    if 'user' not in session:  # 检查用户是否已登录
        return jsonify({"error": "Unauthorized access. Please log in."}), 401

    if 'bucket_name' not in session:
        return jsonify({"error": "No bucket name set"}), 400

    try:
        # 检查原始文件是否存在
        client.get_object(session['bucket_name'], old_image_name)

        # 下载文件到内存并重命名
        response = client.get_object(session['bucket_name'], old_image_name)  # 使用 get_object 而非 fget_object
        data = io.BytesIO(response.read())  # 读取内容到 BytesIO

        # 将数据上传为新的文件名
        data.seek(0)  # 重置指针到开始位置
        length = data.getbuffer().nbytes  # 获取 BytesIO 的长度
        client.put_object(bucket_name, new_image_name, data, length)  # 使用新的文件名进行上传

        # 删除旧文件
        client.remove_object(bucket_name, old_image_name)

        return jsonify({"message": f"Image renamed from '{old_image_name}' to '{new_image_name}'."}), 200
    except S3Error as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/logout')
def logout():
    session.pop('user', None)  # 清除用户会话
    session.pop('bucket_name', None)  # 可选，清除 bucket_name
    return redirect(url_for('home'))  # 登出后重定向到登录页面

if __name__ == '__main__':
    app.run(debug=True)  # 在本地调试模式下运行   