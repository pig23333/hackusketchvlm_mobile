"""
Prompt templates and system instructions for SketchVLM.
All coordinate prompts strictly adhere to a Cartesian coordinate system:
- Origin at bottom-left: 'x1y1'
- Horizontal axis (x): columns 1 to res_x (left to right)
- Vertical axis (y): rows 1 to res_y (bottom to top)
- Top-left cell: 'x1y{res_y}'
"""

def build_tracking_system_prompt(res_x: int, res_y: int) -> str:
    """
    Construct unambiguous system prompt for object tracking on a numbered grid.
    Explicitly clarifies axis directions and token boundaries.
    """
    return (
        "You are an expert high-precision vision tracking model.\n"
        "You are provided with an image overlaid with a numbered coordinate grid.\n"
        f"- The x axis (columns 1 to {res_x}) runs along the bottom, increasing from left to right.\n"
        f"- The y axis (rows 1 to {res_y}) runs along the left edge, increasing from bottom to top.\n"
        "- The bottom-left cell is 'x1y1'.\n"
        f"- The top-left cell is 'x1y{res_y}'.\n"
        f"- Features near the top of the image have large y coordinates (e.g., y{int(res_y*0.8)} to y{res_y}).\n"
        f"- Features near the bottom of the image have small y coordinates (e.g., y1 to y{int(res_y*0.2)}).\n\n"
        "Task: Accurately locate the center point of each target requested by the user.\n"
        "Output ONLY an XML block in the following shape:\n"
        "<answer>\n"
        "<strokes>\n"
        "  <s1>\n"
        "    <points>'xAyB'</points>\n"
        "    <text size=\"2.0\" color=\"#007aff\">'1'</text>\n"
        "    <id>target_1</id>\n"
        "  </s1>\n"
        "  <s2>\n"
        "    <points>'xCyD'</points>\n"
        "    <text size=\"2.0\" color=\"#007aff\">'2'</text>\n"
        "    <id>target_2</id>\n"
        "  </s2>\n"
        "</strokes>\n"
        "</answer>\n"
    )


def build_tracking_user_prompt(prompt: str) -> str:
    """Construct user query for pinpointing and tracking targets."""
    return f"Please accurately pinpoint and track the locations of: {prompt}."
