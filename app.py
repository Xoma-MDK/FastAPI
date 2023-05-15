import uvicorn
from fastapi import FastAPI
from routers import Auth, Messages, User, Avatar
from fastapi.middleware.cors import CORSMiddleware
from settings import title, host, port, origins

app = FastAPI(title=title, docs_url="/api/docs",
              openapi_url="/api/openapi.json", version="1.0")


app.include_router(Auth.auth_route, prefix="/api/auth")
app.include_router(Messages.messages_route, prefix="/api/messages")
app.include_router(User.user_route, prefix="/api/users")
app.include_router(Avatar.avatar_route, prefix="/api/avatar")
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
    uvicorn.run('app:app', port=port,
                host=host, reload=True)
