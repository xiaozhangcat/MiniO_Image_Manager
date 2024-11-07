const apiUrl = 'http:/127.0.0.1:5000/api'; // 替换为实际 API URL

// 获取图片列表
async function fetchImages() {
    const response = await fetch(`${apiUrl}/images`);
    if (!response.ok) {
        const error = await response.json();
        document.getElementById('error-message').innerText = error.error;
        return;
    }
    const images = await response.json();
    const imageListDiv = document.getElementById('image-list');
    imageListDiv.innerHTML = ''; // 清空列表

    images.forEach(image => {
        const imageElement = document.createElement('div');
        imageElement.classList.add('image-item');
        imageElement.innerText = image;
        imageListDiv.appendChild(imageElement);
    });
}

// 重命名图片
async function renameImage() {
    const oldImageName = document.getElementById('oldImageName').value;
    const newImageName = document.getElementById('newImageName').value;

    const response = await fetch(`${apiUrl}/image/rename/${oldImageName}/${newImageName}`, {
        method: 'PUT'
    });

    const messageDiv = document.getElementById('result-message');
    const errorDiv = document.getElementById('error-message');

    if (response.ok) {
        messageDiv.innerText = `Image renamed from '${oldImageName}' to '${newImageName}'.`;
        errorDiv.innerText = '';
        fetchImages(); // 刷新图片列表
    } else {
        const error = await response.json();
        errorDiv.innerText = error.error;
        messageDiv.innerText = '';
    }
}

// 添加事件监听器
document.getElementById('rename-button').addEventListener('click', renameImage);

// 页面加载时获取图片列表
window.onload = fetchImages;