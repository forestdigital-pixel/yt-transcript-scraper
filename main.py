from fastapi import FastAPI, HTTPException
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import os
import uvicorn

app = FastAPI(title="YouTube Transcript Server")

@app.get("/transcript")
def get_transcript(videoId: str, lang: str = "en"):
    try:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(videoId, languages=[lang])
        except NoTranscriptFound:
            transcript_list = YouTubeTranscriptApi.list_transcripts(videoId)
            transcript = transcript_list.find_generated_transcript(
                ["en", "zh-TW", "zh-CN", "ja", "ko"]
            ).fetch()

        return {
            "videoId": videoId,
            "lang": lang,
            "content": [
                {
                    "text": item["text"],
                    "start": item["start"],
                    "dur": item.get("duration", 0)
                }
                for item in transcript
            ]
        }

    except TranscriptsDisabled:
        raise HTTPException(status_code=404, detail="Transcripts are disabled for this video")
    except NoTranscriptFound:
        raise HTTPException(status_code=404, detail="No transcript found for this video")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)