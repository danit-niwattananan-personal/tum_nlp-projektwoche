import textwrap
import os
import time
import requests
from pathlib import Path
from time import sleep

def build_music_prompt(genre: str, scenes: list, prefix: str) -> str:
    """
    Build a single continuous music prompt for the whole trailer based on timestamped segments.
    """
    music_segments = []
    for scene in scenes:
        if scene["music_prompt"]:
            music_segments.append(f"[{scene['start']}–{scene['end']}] {scene['music_prompt']}")

    timeline_description = "\n".join(music_segments)

    return textwrap.dedent(f"""
    {prefix.strip()}

    Music progression:
    {timeline_description.strip()}
    """).strip()

def build_sfx_prompts(genre: str, scenes: list) -> list:
    """
    Build individual sound effect prompts for each scene with timestamps.
    Returns a list of dicts with cleaned prompts.
    """
    sfx_output = []
    for scene in scenes:
        if scene["sfx_prompt"]:
            # Join list of sound effects or use string
            if isinstance(scene["sfx_prompt"], list):
                sfx_body = ", ".join(scene["sfx_prompt"])
            else:
                sfx_body = scene["sfx_prompt"]
            
            # Append clean prompt (only the sound description)
            sfx_output.append({
                "id": scene["id"],
                "scene_title": scene.get("scene_title", f"Scene {scene['id']}"),
                "start": scene["start"],
                "end": scene["end"],
                "sfx_prompt": sfx_body  # clean version
            })

    return sfx_output

def generate_sfx(prompts, genre: str, api_key: str, output_dir="assets/audio/sfx/"):
    """
    Generates sound effects using ElevenLabs API for each scene prompt.
    Saves each output as an .mp3 file.
    """
    os.makedirs(output_dir, exist_ok=True)

    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }

    for prompt in prompts:
        scene_id = prompt['id']
        text_prompt = prompt['sfx_prompt']

        print(f"\n Requesting SFX for Scene {scene_id}...")

        payload = {
            "text": text_prompt,
            "output_format": "mp3_44100_128"  # standard free tier format
        }

        try:
            response = requests.post(
                url="https://api.elevenlabs.io/v1/sound-generation",
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            audio_path = os.path.join(output_dir, f"{genre}_scene_{scene_id:02d}.mp3")
            with open(audio_path, "wb") as f:
                f.write(response.content)

            print(f" Saved: {audio_path}")

        except requests.exceptions.RequestException as e:
            print(f" Error generating SFX for Scene {scene_id}: {e}")