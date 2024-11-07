// 获取图片列表
async function fetchImages() {
    const response = await fetch(`${apiUrl}/api/images`);
    if (!response.ok) {
        let error;
        try{
            error = await response.json();
        }catch (e){
            error = { error: 'Unknow error occurred' };
        }
        document.getElementById('error-message').innerText = error.error;
        return;
    }
    const images = await response.json();
    const imageListDiv = document.getElementById('image-list');
    imageListDiv.innerHTML = ''; // 清空列表

    images.forEach(image => {
        const imageElement = document.createElement('div');
        imageElement.classList.add('image-item');
        // 创建一个链接，使其点击后打开对应的图片
        imageElement.innerHTML = `<a href="${apiUrl}/api/image/${encodeURIComponent(image)}" target="_blank">${image}</a>`;
        imageListDiv.appendChild(imageElement);
    });
}

// 重命名图片
async function renameImage() {
    const oldImageName = document.getElementById('oldImageName').value;
    const newImageName = document.getElementById('newImageName').value;

    const response = await fetch(`${apiUrl}/api/image/rename/${oldImageName}/${newImageName}`, {
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