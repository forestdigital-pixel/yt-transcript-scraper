from fastapi import FastAPI, HTTPException
from youtube_transcript_api import YouTubeTranscriptApi
import os
import uvicorn

app = FastAPI(title="YouTube Transcript Server")

@app.get("/transcript")
def get_transcript(videoId: str, lang: str = "en"):
    try:
        ytt = YouTubeTranscriptApi()
        
        # Fetch transcript list for the video
        transcript_list = ytt.list(videoId)

        # Try to find transcript in requested language
        try:
            transcript = transcript_list.find_transcript([lang])
        except Exception:
            # Fall back to any available transcript
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