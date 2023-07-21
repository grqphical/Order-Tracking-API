import uvicorn
from dotenv import load_dotenv
import os

load_dotenv()

if __name__ == "__main__":
    uvicorn.run(
        "order_api.main:app",
        port=9000,
        reload=True if os.environ.get("DEBUG") == "TRUE" else False,
    )
