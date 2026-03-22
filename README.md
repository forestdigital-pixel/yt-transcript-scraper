# YouTube Transcript Server

A lightweight FastAPI server that fetches YouTube video transcripts using `youtube-transcript-api`. Designed to be deployed on Railway.app and called from n8n workflows.

---

## Files

| File | Purpose |
|---|---|
| `main.py` | FastAPI server code |
| `requirements.txt` | Python dependencies |
| `Procfile` | Tells Railway how to start the server |

---

## Deploy to Railway

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "transcript server"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/transcript-server.git
git push -u origin main
```

### 2. Deploy on Railway
1. Go to https://railway.app → Sign up with GitHub
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your `transcript-server` repo
4. Railway auto-detects Python and deploys automatically
5. Go to **Settings** → **Networking** → **Generate Domain**
6. Copy your public URL

### 3. Set Environment Variables (Optional but Recommended)
In Railway dashboard → **Variables**, add:
```
API_KEY = any_secret_string_you_choose
```
This protects your server so only your n8n can call it.

---

## API Endpoints

### GET /transcript
Fetch transcript for a YouTube video.

**Parameters:**
- `videoId` (required) — YouTube video ID e.g. `dQw4w9WgXcQ`
- `lang` (optional) — Language code, default `en`

**Headers:**
- `x-api-key` — Your API key (if set in environment variables)

**Example:**
```
GET https://your-server.up.railway.app/transcript?videoId=dQw4w9WgXcQ&lang=en
```

**Response:**
```json
{
  "videoId": "dQw4w9WgXcQ",
  "lang": "en",
  "content": [
    { "text": "Hello", "start": 0.0, "dur": 1.5 },
    { "text": "welcome", "start": 1.5, "dur": 2.0 }
  ]
}
```

### GET /health
Check if server is running.
```
GET https://your-server.up.railway.app/health
```
```json
{ "status": "ok" }
```

---

## n8n Fetch Transcripts Node Code

```javascript
const item = $input.all()[0];
const videoId = item.json.video_id;
const SERVER_URL = 'https://your-server.up.railway.app';
const API_KEY = 'your_secret_key'; // match what you set in Railway variables

try {
  const res = await helpers.httpRequest({
    method: 'GET',
    url: `${SERVER_URL}/transcript?videoId=${videoId}&lang=en`,
    returnFullResponse: true,
    headers: {
      'x-api-key': API_KEY
    }
  });

  const body = res.body;
  const chunks = (body.content || []).map(c => ({
    start: c.start,
    duration: c.dur,
    text: c.text
  }));

  return [{
    json: {
      ...item.json,
      data: chunks,
      lang_used: body.lang || 'en',
      caption_status: chunks.length > 0 ? 'found' : 'no_captions'
    }
  }];

} catch (error) {
  return [{
    json: {
      ...item.json,
      data: [],
      full_caption: '',
      caption_status: `error: ${error.message}`
    }
  }];
}
```

---

## Supported Languages
- `en` — English
- `zh-TW` — Traditional Chinese
- `zh-CN` — Simplified Chinese
- `ja` — Japanese
- `ko` — Korean
