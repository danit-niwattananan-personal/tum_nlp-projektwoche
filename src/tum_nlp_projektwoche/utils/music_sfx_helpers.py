import textwrap

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

def build_sfx_prompts(genre: str, scenes: list, prefix: str) -> list:
    """
    Build individual sound effect prompts for each scene with timestamps.
    Returns a list of dicts for easy export or display.
    """
    sfx_output = []
    for scene in scenes:
        # Accept both string and list formats for sfx_prompt
        if scene["sfx_prompt"]:
            if isinstance(scene["sfx_prompt"], list):
                sfx_body = "\n".join(f"- {line}" for line in scene["sfx_prompt"])
            else:
                sfx_body = f"- {scene['sfx_prompt']}"
            
            full_prompt = f"{prefix.strip()}\n\nScene: {scene['scene_title']}\nSound Design:\n{sfx_body}"
            
            sfx_output.append({
                "id": scene["id"],
                "start": scene["start"],
                "end": scene["end"],
                "sfx_prompt": full_prompt
            })

    return sfx_output
