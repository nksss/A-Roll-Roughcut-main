# A-Roll Rough Cut

<img width="2511" height="1278" alt="dashBoard" src="https://github.com/user-attachments/assets/38fa61fc-24b1-4e1f-aa9f-b3bcbd79dfda" />


Remove false starts and stumbles from talking-head footage while preserving natural pauses between sentences. Review the cuts in a browser, then export subtitles aligned to the edited timeline or a fixed-frame-rate video for Jianying/CapCut.

Prepare a source video and, if available, its script. Open this repository in Cursor, Claude Code, or Codex. The agent follows [koubo-roughcut/SKILL.md](koubo-roughcut/SKILL.md) to transcribe, compare, and make conservative cut decisions. Decisions are stored in `cut_decisions.json` and can be edited in the browser review panel.

## Features

- Remove failed starts and repeated takes while preserving natural pauses
- Listen to the edited result in the browser and restore or remove words
- Export SRT subtitles aligned to the edited timeline and a fixed-frame-rate MP4

This workflow ends at the approved rough cut. B-roll, sound effects, and Jianying/CapCut project files are out of scope.

## Installation

### Option 1: Ask an agent to install

Give your coding agent this repository URL and ask it to install the project:

```text
https://github.com/nksss/A-Roll-Roughcut-main
```

The agent will read this README, install ffmpeg and the Python environment, and run the setup check.

You will need a Bailian API key. Create or copy one using the [Alibaba Cloud Model Studio API key guide](https://help.aliyun.com/zh/model-studio/get-api-key). Keys start with `sk-`. For mainland China, use `https://dashscope.aliyuncs.com`. During setup, put the key in the repository-root `.env` file. Do not paste it into a chat:

```dotenv
DASHSCOPE_API_KEY=sk-your-key
```

The setup check prints `ok` when everything is ready.

### Option 2: Install manually

Run these commands from the repository root.

**1. Install ffmpeg**

On macOS with Homebrew:

```bash
brew install ffmpeg
```

On other systems, install ffmpeg and make sure both `ffmpeg` and `ffprobe` are available on your `PATH`.

**2. Configure the Bailian API key**

Add the key to the repository-root `.env` file:

```dotenv
DASHSCOPE_API_KEY=sk-your-key
```

Alternatively, set it for the current shell session:

```bash
export DASHSCOPE_API_KEY=sk-your-key
```

Only add `DOUBAO_SPEECH_API_KEY` if you explicitly choose Doubao Speech Recognition 2.0. The default transcription engine is Bailian `paraformer-v2`.

**3. Create a Python environment and install dependencies**

Windows PowerShell:

```powershell
py -3 -m venv koubo-roughcut/.venv
koubo-roughcut/.venv/Scripts/python.exe -m pip install -r koubo-roughcut/scripts/requirements.txt
```

Linux and macOS:

```bash
python3 -m venv koubo-roughcut/.venv
koubo-roughcut/.venv/bin/python -m pip install -r koubo-roughcut/scripts/requirements.txt
```

The `.venv` directory is not tracked by Git. Create it separately on each machine.

**4. Run the setup check**

Windows PowerShell:

```powershell
koubo-roughcut/.venv/Scripts/python.exe koubo-roughcut/scripts/setup_check.py
```

Linux and macOS:

```bash
koubo-roughcut/.venv/bin/python koubo-roughcut/scripts/setup_check.py
```

The check prints `ok` when setup is complete. Otherwise, it lists missing tools, packages, or keys.

## Create a rough cut

1. Create a project directory under `koubo-roughcut/workspace/`, using a recognizable name, for example `koubo-roughcut/workspace/my-video/`.
2. Put the source video in that directory. Keep its original filename.
3. Add a `脚本.md` file to the same directory, if a script is available.
4. Ask your agent to make a first-pass talking-head rough cut for `my-video`.
5. The review page opens at `http://127.0.0.1:8765/` and starts with edited playback. Playback rates are 1.0, 1.1, 1.2, and 1.3. Adjust cuts in the page, then export subtitles or video. Save before exporting.

You can start without a script. The agent will remove repetitions based on the spoken content and note that no script comparison was performed.

Each run is stored in `koubo-roughcut/workspace/<project-name>/runs/<date>/`. This run directory can be deleted and regenerated from the source video, `脚本.md`, and the skill.

### Reopen an existing review

Use the launcher for your platform. At startup, enter the project directory (the directory containing `runs/`). The launcher selects the latest run by sorting run-directory names in descending order and opens the review page at `http://127.0.0.1:8765/`:

- Windows: double-click `koubo-roughcut/scripts/start_review_windows.bat`
- Linux: from the repository root, run `bash koubo-roughcut/scripts/start_review_linux.sh`
- macOS: double-click `koubo-roughcut/scripts/start_review_mac.command`. If macOS blocks it, run `chmod +x koubo-roughcut/scripts/start_review_mac.command` in Terminal first.

Enter either a path relative to the repository root or an absolute path. For example: `koubo-roughcut/workspace/my-video`. Use `YYYY-MM-DD` for run-directory names so reverse name sorting selects the most recent date. The launchers require the `koubo-roughcut/.venv` environment. Keep the terminal window open while reviewing; press `Ctrl+C` there to stop the server.

The review server attempts to locate the source video from the selected run's decisions file.

### Learn preferences (only when requested)

Only analyze review differences and turn them into preference rules when the user explicitly asks. Summarize the differences first, then record the confirmed preference.

## Data and privacy

The review server listens only on `127.0.0.1`; the review page is not exposed outside this computer.

Transcription is the only step that sends data off-device:

- By default, local audio is sent to Alibaba Cloud Model Studio for speech recognition. The script uses `https://dashscope.aliyuncs.com/api/v1` to request an upload, submit the job, and retrieve the transcript. The audio is uploaded to a temporary URL provided by Bailian.
- Doubao is contacted at `https://openspeech.bytedance.com` only when explicitly selected. For that workflow, the audio must already be available at a URL Doubao can download.

Keep API keys in environment variables or the repository-root `.env` file. Do not put them in source code, skills, commits, or review logs. Source videos, `.venv`, temporary WAV files, and rough-cut MP4 files are not tracked by Git.

The repository does not include usage analytics or a project-owned server. To use another Bailian region, set `DASHSCOPE_HTTP_BASE_URL`; otherwise, the mainland China endpoint above is used.

## Directory layout

| Path | Contents |
|---|---|
| `koubo-roughcut/` | Rough-cut skill and references |
| `koubo-roughcut/scripts/` | Transcription, validation, review, and export scripts |
| `koubo-roughcut/workspace/<project-name>/脚本.md` | Talking-head script |
| `koubo-roughcut/workspace/<project-name>/` | Original source video and project files |
| `koubo-roughcut/workspace/<project-name>/runs/<date>/` | Outputs from one rough-cut run |

## Source of truth

Use this README for installation and getting started. The workflow, editing rules, and deliverables are defined in [koubo-roughcut/SKILL.md](koubo-roughcut/SKILL.md). Changes to the rules are recorded in [koubo-roughcut/note.md](koubo-roughcut/note.md).

## License

[MIT](LICENSE)
