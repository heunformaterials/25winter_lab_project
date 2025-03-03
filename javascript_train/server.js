const express = require('express');
const app = express();
const PORT = process.env.PORT || 80;

// 기본 라우트 설정
app.get('/', (req, res) => {
    res.send('Server is running!');
});

// 서버 실행
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on port ${PORT}`);
});
