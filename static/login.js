const loginUrl = 'http://127.0.0.1:5000/login';  // 登录 API 的 URL
const imageManagerUrl = 'http://127.0.0.1:5000/index';  // 图像管理页面的 URL

document.getElementById('loginForm').addEventListener('submit', async (event) => {
    event.preventDefault();  // 防止表单提交

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        // 发送登录请求 `${apiUrl}/api/images`
        const response = await fetch(loginUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        if (!response.ok) {
            throw new Error('Invalid username or password');
        }

        window.location.href = imageManagerUrl;  // 登录成功，重定向到图像管理页面
    } catch (error) {
        document.getElementById('error-message').innerText = `Error: ${error.message}`;  // 显示错误信息
    }
});