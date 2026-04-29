---
did: skill:007
version: "1.0.0"
created: "2026-04-29"
name: autonomyx-music-player
description: >
  Builds a production-grade interactive music player as an HTML artifact with Autonomyx branding.
  Four modes in one tabbed widget: (1) Upload & Play — local audio files with waveform oscilloscope
  visualizer; (2) Stream from URL — direct mp3/ogg/wav URLs with the same visualizer and CORS fallback;
  (3) Mood Playlist — describe a mood or activity, get 10 AI-curated track suggestions with YouTube
  and SoundCloud search links; (4) Search & Play — search by artist or track name, get 6 results with
  thumbnails, embed YouTube iframe to play in-player, fallback to search link when ID is uncertain.
  Always trigger when: "music player", "audio player", "play this audio", "stream this mp3",
  "waveform visualizer", "playlist for my mood", "songs for studying/working out",
  "search YouTube music", "build me a player", "I want to listen to", user uploads an audio file,
  or any request for an audio UI widget, playlist generator, or YouTube music search.
---

# Autonomyx Music Player

Builds a unified, visually striking music player artifact. Three modes in one widget:

- **Upload & Play** — local audio files, waveform oscilloscope visualizer
- **Stream from URL** — direct audio URLs or SoundCloud/podcast links
- **Mood Playlist** — AI-curated track suggestions with search links (no autoplay)

---

## Step 1 — Determine Mode(s) Needed

Infer from context which mode(s) to activate. If ambiguous, build all three tabs.

| Signal | Mode |
|---|---|
| User uploads an audio file | Upload & Play |
| User pastes a URL ending in `.mp3`, `.ogg`, `.wav`, or a SoundCloud/podcast link | Stream from URL |
| User describes a mood, genre, activity, or emotion | Mood Playlist |
| No specific signal | Build all three tabs |

---

## Step 2 — Aesthetic Direction

Autonomyx brand palette applies as a baseline:
- **Primary**: Autonomyx Blue `#1B5EBE`
- **Background**: Deep Navy `#001141`
- **Font**: IBM Plex Sans / IBM Plex Mono
- **Accent**: Electric cyan `#00CFFF` for the waveform and active states

Aesthetic direction: **dark, precision-instrument UI** — like a high-end DAW or studio monitor. Not a consumer app. Think oscilloscope + cinematic dark mode. Avoid gradients-on-white, generic player chrome, or anything that looks like a podcast app.

Key visual moments:
- Waveform oscilloscope rendered on `<canvas>` using Web Audio API `AnalyserNode`
- Track card hover states with a subtle glow in Autonomyx Blue
- Playlist mood cards with genre tags rendered as monospace pills
- Smooth tab transitions (CSS only, no library needed)

---

## Step 3 — Build the Artifact

Produce a **single self-contained HTML file** (no external dependencies except Google Fonts for IBM Plex Sans via `@import`).

### Upload & Play Tab

```
- Drag-and-drop zone OR file input (accepts audio/*)
- Displays: track name (filename), duration
- Controls: Play/Pause, Seek bar (styled range input), Volume, Current time / Total time
- Waveform: <canvas> oscilloscope — draws the time-domain waveform of the live audio signal
  - Uses: AudioContext → MediaElementSourceNode → AnalyserNode → canvas requestAnimationFrame loop
  - Waveform color: #00CFFF on #001141 background
  - When paused: freeze last frame, reduce opacity to 40%
- Multiple files: show a queue list below the player; click to switch tracks
```

### Stream from URL Tab

```
- Text input: accepts direct audio URL (mp3/ogg/wav/aac) or any URL the browser <audio> tag can handle
- "Load & Play" button
- Same player controls and waveform visualizer as Upload tab
- Error state: if URL fails to load (CORS or unsupported), show a clear inline error:
  "This URL couldn't be loaded directly. SoundCloud and some sites block direct embedding —
   try a direct .mp3 link or download the file and use the Upload tab."
- Do NOT attempt SoundCloud oEmbed or iframe embedding — browser security will block it.
  Just display a friendly fallback card with a "Open in SoundCloud →" link button instead.
```

### Mood Playlist Tab

```
- Textarea: "Describe a mood, activity, or vibe..."
- "Generate Playlist" button → calls Claude API (claude-sonnet-4-20250514) with a system prompt
  that returns JSON: array of { title, artist, year, tags[], youtubeSearchUrl, soundcloudSearchUrl, reason }
- Render each track as a card:
  - Track title + artist (IBM Plex Sans Bold)
  - Year + tag pills (monospace, Autonomyx Blue border)
  - Two link buttons: [▶ YouTube] [☁ SoundCloud] — open in new tab
  - Short reason line in muted text: why this track fits the mood
- Show 8–12 tracks per playlist
- "Regenerate" button re-runs with a different seed instruction
- Loading state: animated waveform placeholder bars (CSS keyframes)
```

### Search & Play Tab (4th tab)

```
- Search input + "SEARCH" button
- Calls Claude API to generate a list of 6 YouTube search results for the query:
  { title, artist, year, description, youtubeId (best-guess), youtubeSearchUrl }
- Claude infers the most likely YouTube video ID from its training knowledge where confident;
  falls back to a search URL where not confident (youtubeId: null)
- Result cards: thumbnail (via img.youtube.com/vi/{id}/hqdefault.jpg), title, artist, year, description
- Clicking a card with a known youtubeId: embeds youtube.com/embed/{id} in an iframe below the results
  - iframe: 100% width, 360px height, allowfullscreen, no border
  - replaces previous embed (one active at a time)
- Clicking a card with no youtubeId: opens youtubeSearchUrl in a new tab
- Active card highlighted with Autonomyx Blue border + glow
- "OPEN ON YOUTUBE →" button below the iframe for the active track
- Note in skill: YouTube IDs are inferred — they may occasionally be wrong. The fallback
  search URL is always provided so users can find the correct video themselves.
```

---

## Step 4 — Claude API Call for Mood Playlist

Use the Anthropic API from inside the artifact:

```javascript
const response = await fetch("https://api.anthropic.com/v1/messages", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    model: "claude-sonnet-4-20250514",
    max_tokens: 1000,
    system: `You are a music curator. Return ONLY a JSON array of 10 track objects. No markdown, no explanation.
Each object: { "title": string, "artist": string, "year": number, "tags": string[],
"youtubeSearchUrl": string, "soundcloudSearchUrl": string, "reason": string }
youtubeSearchUrl = "https://www.youtube.com/results?search_query=" + encodeURIComponent(artist + " " + title)
soundcloudSearchUrl = "https://soundcloud.com/search?q=" + encodeURIComponent(artist + " " + title)
reason = one sentence: why this track fits the mood.`,
    messages: [{ role: "user", content: `Generate a playlist for this mood: ${moodInput}` }]
  })
});
```

Parse `data.content[0].text` → `JSON.parse()` → render cards. Wrap in try/catch; show inline error on failure.

---

## Step 5 — Quality Checklist

Before finalising the artifact, verify:

- [ ] Web Audio API waveform animates during playback (requestAnimationFrame loop)
- [ ] Waveform freezes (not blank) on pause
- [ ] Seek bar updates in real time; clicking it seeks correctly
- [ ] Volume slider works
- [ ] Tab switching preserves player state (don't reset audio on tab change)
- [ ] Mood playlist cards render with both link buttons
- [ ] CORS failure on Stream tab shows friendly error, not a broken UI
- [ ] IBM Plex Sans loads from Google Fonts
- [ ] Full dark theme — no white backgrounds anywhere
- [ ] Autonomyx wordmark + tagline in footer: "Autonomyx · From Foundational To Frontier: FullStack AI"

---

## Edge Cases

| Situation | Handling |
|---|---|
| Browser blocks AudioContext before user gesture | Create AudioContext inside the first play() click handler, not on load |
| File has no ID3 metadata | Use filename (strip extension) as track name |
| Mood input is very short (e.g. "sad") | Claude still generates — brief inputs are valid |
| User pastes a YouTube URL | Inform: "YouTube links can't be streamed directly. Use the Mood Playlist tab to find it." |
| Multiple files queued, user deletes one | Remove from queue array, if it was playing, advance to next |

---

## Output

A single downloadable `.html` file presented via `present_files`. Also renders inline as an artifact if the environment supports it.

Always end with: "You can upload audio files, paste a stream URL, or describe a mood to generate a playlist. All three modes are in the tabs above."
