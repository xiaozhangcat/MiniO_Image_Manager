from flask import Flask, jsonify, send_file
from minio import Minio
from minio.error import S3Error
import io
import os

app = Flask(__name__)

# MinIO 配置
MINIO_URL = 'you_url'
ACCESS_KEY = 'you_access_key'
SECRET_KEY = 'you_secret_key'
BUCKET_NAME = 'you_bucket'

# 创建 MinIO 客户端
client = Minio(MINIO_URL, access_key=ACCESS_KEY, secret_key=SECRET_KEY, secure=False)

@app.route('/api/images', methods=['GET'])
def list_images():
    try:
        images = []
        objects = client.list_objects(BUCKET_NAME, recursive=True)
        for obj in objects:
            if obj.object_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                images.append(obj.object_name)

        return jsonify(images)
    except S3Error as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/image/<string:image_name>', methods=['GET'])
def get_image(image_name):
    try:
        response = client.get_object(BUCKET_NAME, image_name)
        return send_file(io.BytesIO(response.read()), mimetype='image/jpeg')
    except S3Error as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/image/rename/<string:old_image_name>/<string:new_image_name>', methods=['PUT'])
def rename_image(old_image_name, new_image_name):
    try:
        # 检查原始文件是否存在
        client.get_object(BUCKET_NAME, old_image_name)
        # 下载文件到内存并重命名
        data = io.BytesIO()
        client.fget_object(BUCKET_NAME, old_image_name, data)

        # 将数据上传为新的文件名
        data.seek(0)  # 重置指针到开始位置
        client.put_object(BUCKET_NAME, new_image_name, data, data.seek(0, os.SEEK_END)) # 使用新的文件名进行上传

        # 删除旧文件
        client.remove_object(BUCKET_NAME, old_image_name)

        return jsonify({"message": f"Image renamed from '{old_image_name}' to '{new_image_name}'."}), 200
    except S3Error as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)  # 在本地调试模式下运行   