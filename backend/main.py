from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from supertokens_python import init, InputAppInfo, SupertokensConfig
from supertokens_python.recipe import emailpassword, session
from supertokens_python.framework.fastapi import get_middleware
from supertokens_python.recipe.session.framework.fastapi import verify_session
from supertokens_python.recipe.session import SessionContainer
from .routes import router
import os

# Initialize SuperTokens
init(
    app_info=InputAppInfo(
        app_name="Park Place",
        api_domain="http://localhost:8000",
        website_domain="http://localhost:3000",
        api_base_path="/auth",
        website_base_path="/auth"
    ),
    supertokens_config=SupertokensConfig(
        connection_uri="http://localhost:3567",
        # For production, add: api_key=os.getenv("SUPERTOKENS_API_KEY")
    ),
    framework='fastapi',
    recipe_list=[
        emailpassword.init(),
        session.init(
            cookie_domain="localhost",
            cookie_secure=False,  # Set to True in production with HTTPS
        )
    ]
)

app = FastAPI(title="Park Place API", version="1.0.0")

# Add SuperTokens middleware
app.add_middleware(get_middleware())

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Public endpoint for testing
@app.get("/api/public")
async def public_endpoint():
    return {"message": "This is a public endpoint"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
