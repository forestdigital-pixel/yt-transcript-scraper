from fastapi import FastAPI, HTTPException
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
import os
import uvicorn

app = FastAPI(title="YouTube Transcript Server")

# Webshare proxy credentials — set these in Railway Variables
PROXY_USERNAME = os.environ.get("PROXY_USERNAME", "")
PROXY_PASSWORD = os.environ.get("PROXY_PASSWORD", "")

@app.get("/transcript")
def get_transcript(videoId: str, lang: str = "en"):
    try:
        # Use proxy to bypass YouTube IP block
        if PROXY_USERNAME and PROXY_PASSWORD:
            ytt = YouTubeTranscriptApi(
                proxy_config=WebshareProxyConfig(
                    proxy_username=PROXY_USERNAME,
                    proxy_password=PROXY_PASSWORD,
                )
            )
        else:
            ytt = YouTubeTranscriptApi()

        transcript_list = ytt.list(videoId)

        try:
            transcript = transcript_list.find_transcript([lang])
        except Exception:
            transcript = transcript_list.find_generated_transcript(
                ["en", "zh-TW", "zh-CN", "ja", "ko"]
            )

        fetched = transcript.fetch()

        return {
            "videoId": videoId,
            "lang": transcript.language_code,
            "content": [
                {
                    "text": item.text,
                    "start": item.start,
                    "dur": item.duration
                }
                for item in fetched
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
