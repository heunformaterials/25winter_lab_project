require("dotenv").config();
const express = require("express");
const axios = require("axios");

const app = express();
const PORT = process.env.PORT || 80;  // 80번 포트 사용

app.use(express.static("public"))

const NOTION_API_KEY = process.env.NOTION_API_KEY;
const DATABASE_ID = process.env.NOTION_DATABASE_ID;
const NOTION_URL = `https://api.notion.com/v1/databases/${DATABASE_ID}/query`;

app.use(express.static("public")); // 정적 파일(css, js) 사용 가능

async function getPageContent(pageId) {
    let content = [];
    let hasMore = true;
    let nextCursor = null;

    while (hasMore) {
        try {
            const blocksResponse = await axios.get(`https://api.notion.com/v1/blocks/${pageId}/children`, {
                headers: {
                    Authorization: `Bearer ${NOTION_API_KEY}`,
                    "Notion-Version": "2022-06-28",
                    "Content-Type": "application/json"
                },
                params: nextCursor ? { start_cursor: nextCursor } : {}
            });

            const blocks = blocksResponse.data.results;
            nextCursor = blocksResponse.data.next_cursor;
            hasMore = blocksResponse.data.has_more;

            blocks.forEach(block => {
                let text = "";

                // 🔹 텍스트 변환 함수 (링크 + 멘션 처리)
                const formatRichText = (richTextArray) => {
                    return richTextArray.map(t => {
                        if (t.type === "text") {
                            if (t.text.link) {
                                return `<a href="${t.text.link.url}" target="_blank">${t.text.content}</a>`;
                            }
                            return t.text.content;
                        } else if (t.type === "mention" && t.mention.type === "link_preview") {
                            return `<a href="${t.mention.link_preview.url}" target="_blank">${t.plain_text}</a>`;
                        }
                        return t.plain_text;
                    }).join(" ");
                };

                // 🔹 각 블록 유형별 처리
                if (block.type === "paragraph") {
                    text = formatRichText(block.paragraph.rich_text);
                } else if (block.type === "bulleted_list_item") {
                    text = "• " + formatRichText(block.bulleted_list_item.rich_text);
                } else if (block.type === "heading_1" || block.type === "heading_2" || block.type === "heading_3") {
                    text = `<strong>${formatRichText(block[block.type].rich_text)}</strong>`;
                }

                if (text) {
                    content.push(text);
                }
            });

        } catch (error) {
            console.error(`🚨 페이지(${pageId})의 블록 데이터를 불러오지 못했습니다:`, error.message);
            hasMore = false;
        }
    }

    return content.length > 0 ? content.join("<br>") : "📌 내용 없음";
}


// 📌 기본 페이지 (홈)
app.get("/", async (req, res) => {
    try {
        const response = await axios.post(NOTION_URL, {}, {
            headers: {
                Authorization: `Bearer ${NOTION_API_KEY}`,
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json"
            }
        });

        console.log("🚀 Notion API 응답 데이터:", JSON.stringify(response.data, null, 2));

        // 📌 Notion 데이터 정리 (데이터가 없을 경우 예외 처리 추가)
        const pages = await Promise.all(response.data.results.map(async (page) => {
    const titlePropertyKey = Object.keys(page.properties).find(
        key => page.properties[key].type === "title"
    );

    const titleProperty = titlePropertyKey ? page.properties[titlePropertyKey]?.title || [] : [];
    const title = titleProperty.length > 0 ? titleProperty[0]?.text?.content : "Untitled";

    // 페이지 ID
    const pageId = page.id;

    // 🔥 Notion 페이지 내용 가져오기
    const content = await getPageContent(pageId);

    return { id: pageId, title, content };
}));



        console.log("✅ 변환된 Notion 데이터:", pages); // 가공된 데이터 확인

        // 📌 HTML로 렌더링
let html = `
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Notion 데이터베이스</title>
        <link rel="stylesheet" href="/styles.css">
    </head>
    <body>
        <div class="container">
            <h1>📋 Notion 일기</h1>
            <ul>
                ${pages.length > 0 ? pages.map(page => `
                    <li class="card">
                        <h2>${page.title}</h2>             
                        <div class="content">
                            <p><strong>내용:</strong></p>
                            <p>${page.content ? page.content.replace(/\n/g, "<br>") : "📌 내용 없음"}</p>
                        </div>
                    </li>
                `).join("") : "<p>❌ 데이터가 없습니다.</p>"}
            </ul>
        </div>
    </body>
    </html>
`;
        console.log("🚀 최종 HTML:", html); // 최종 HTML 확인
        res.send(html);
    } catch (error) {
        console.error("🚨 Notion API 요청 오류:", error.response?.data || error.message);
        res.status(500).send("<h1>Notion API 요청 실패</h1><p>오류가 발생했습니다.</p>");
    }
});


// 서버 실행
app.listen(PORT, () => {
    console.log(`🚀 서버 실행: http://localhost:${PORT}`);
});

