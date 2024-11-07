const apiUrl = 'http://127.0.0.1:5000'; // 替换为实际 API URL

document.getElementById('submit-bucket').addEventListener('click', async () => {
    const bucketName = document.getElementById('bucket-name').value;
    document.getElementById('error-message').innerText = '';
    const response = await fetch(`${apiUrl}/set_bucket`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ bucket_name: bucketName })
    });

    if (response.ok) {
        alert("Bucket name set successfully!");
        // 继续进行你的操作，如获取图片列表等
        fetchImages();
    } else {
        const error = await response.json();
        document.getElementById('error-message').innerText = error.error;
    }
});

