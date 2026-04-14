from fastapi import FastAPI
from scrapling import Fetcher
import uvicorn

app = FastAPI()

@app.get("/fetch")
def fetch_url(url: str):
    try:
        fetcher = Fetcher(impersonate='chrome')
        resp = fetcher.get(url)
        
        # 终极调试：尝试几种可能的属性
        # Scrapling 的文档显示它返回的是一个封装好的对象
        content = ""
        if hasattr(resp, 'body'):
            content = resp.body
        elif hasattr(resp, 'text'):
            content = resp.text
        else:
            # 如果都找不到，强制转换为字符串看看
            content = str(resp)

        return {
            "status": resp.status,
            "text": content
        }
    except Exception as e:
        return {"status": 500, "text": f"DEBUG_ERROR: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
