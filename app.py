import uvicorn
from fastapi import FastAPI
from routers import Auth, Messages, User
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI( title="FastAPI Chat", docs_url="/api/docs", openapi_url="/api/openapi.json", version="1.0", debug=True)

origins = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8123",
]

app.include_router(Auth.auth_route, prefix="/api/auth")
app.include_router(Messages.messages_route, prefix="/api/messages")
app.include_router(User.user_route, prefix="/api/users")
app.add_middleware(
        CORSMiddleware,
        allow_origins=origins, 
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )



@app.get("/")
async def root():
    return "API сервер Chat"



if __name__ == "__main__":
    uvicorn.run('app:app', port=8123,
                host="0.0.0.0", reload=True)