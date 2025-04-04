from fastapi import FastAPI
import uvicorn
from starlette.responses import HTMLResponse

app = FastAPI()

@app.get('/api/')
async def read_root():
    return {'message': 'Hello World'}

@app.get('/', response_class=HTMLResponse)
async def read_root():
    html_content = """
        <html>
            <head>
                <title>Simple Page</title>
            </head>
            <body>
                <h1>Record Sound</h1>
                <button>record</button>
            </body>
        </html>
        """
    return HTMLResponse(content=html_content, status_code=200)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8800)