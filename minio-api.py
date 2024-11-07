from flask import Flask, jsonify, send_file, render_template, request
from minio import Minio
from minio.error import S3Error
import io


app = Flask(__name__)

# MinIO 配置
MINIO_URL = 'you_path'
ACCESS_KEY = 'you_key'
SECRET_KEY = 'you_key'

# 创建 MinIO 客户端
client = Minio(MINIO_URL, access_key=ACCESS_KEY, secret_key=SECRET_KEY, secure=False)

bucket_name = None

@app.route('/')
def index():
    return render_template('index.html')  # 返回 index.html 页面

@app.route('/set_bucket', methods=['POST'])
def set_bucket():
    global bucket_name
    data = request.get_json()
    bucket_name = data.get('bucket_name')  # 获取从前端发送的 BUCKET_NAME
    if not bucket_name:
        return jsonify({"error": "Bucket name is required."}), 400
    return jsonify({"message": f"Bucket name set to {bucket_name}"}), 200

@app.route('/api/images', methods=['GET'])
def list_images():
    try:
        images = []
        objects = client.list_objects(bucket_name, recursive=True)
        for obj in objects:
            if obj.object_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                images.append(obj.object_name)

        return jsonify(images)
    except S3Error as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/image/<string:image_name>', methods=['GET'])
def get_image(image_name):
    try:
        response = client.get_object(bucket_name, image_name)
        return send_file(io.BytesIO(response.read()), mimetype='image/jpeg')
    except S3Error as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/image/rename/<string:old_image_name>/<string:new_image_name>', methods=['PUT'])
def rename_image(old_image_name, new_image_name):
    try:
        # 检查原始文件是否存在
        client.get_object(bucket_name, old_image_name)

        # 下载文件到内存并重命名
        response = client.get_object(bucket_name, old_image_name)  # 使用 get_object 而非 fget_object
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

if __name__ == '__main__':
    app.run(debug=True)  # 在本地调试模式下运行   