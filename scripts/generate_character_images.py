#!/usr/bin/env python3
"""Generate character images with different expressions and actions using Gemini Edit Images API.

This script is independent of mini_ema and generates anime-style character portraits
based on the original Ema avatar image. It creates variations with different expressions
and actions for use in the chat interface.
"""

import os
import sys
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from google import genai
from PIL import Image


# Expression and action types from PrettyGeminiBot
Expression = Literal["neutral", "smile", "serious", "confused", "surprised", "sad"]
Action = Literal["none", "nod", "shake", "wave", "jump", "point"]

# All possible expressions and actions
EXPRESSIONS: list[Expression] = ["neutral", "smile", "serious", "confused", "surprised", "sad"]
ACTIONS: list[Action] = ["none", "nod", "shake", "wave", "jump", "point"]


def load_api_key() -> str:
    """Load Gemini API key from environment.

    Returns:
        API key string

    Raises:
        ValueError: If API key is not found
    """
    # Try to load from .env file in project root
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found in environment. Please set it in .env file or environment variables."
        )
    return api_key


def generate_character_image(
    client: genai.Client,
    base_image: Image.Image,
    expression: Expression,
    action: Action,
    output_path: Path,
) -> bool:
    """Generate a character image with specified expression and action.

    Args:
        client: Gemini API client
        base_image: Base character image (Ema avatar)
        expression: Facial expression to generate
        action: Physical action to generate
        output_path: Path to save the generated image

    Returns:
        True if generation was successful, False otherwise
    """
    # Create prompt for image editing
    action_desc = f" doing a {action} action" if action != "none" else ""
    prompt = f"""Edit this anime character portrait to show the character with a {expression} expression{action_desc}.

Keep the character's appearance and style exactly the same, only change the facial expression and pose.
Make it a clean, professional anime-style portrait suitable for a chat interface avatar.
The character should be looking at the viewer."""

    try:
        print(f"  Generating {expression} + {action}...", end=" ", flush=True)

        # Create chat session for image editing
        chat = client.chats.create(model="gemini-2.5-flash-image")

        # Send the image and prompt
        response = chat.send_message([prompt, base_image])

        # Check if response has candidates
        if not response.candidates:
            print("✗ (no candidates in response)")
            return False

        # Save the generated image
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                image = part.as_image()
                image.save(output_path)
                print("✓")
                return True

        print("✗ (no image in response)")
        return False

    except Exception as e:
        print(f"✗ (error: {str(e)})")
        return False


def main():
    """Main function to generate all character image variations."""
    # Setup paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    base_image_path = project_root / "assets" / "imgs" / "ema.png"
    output_dir = project_root / "assets" / "gen_imgs"

    # Verify base image exists
    if not base_image_path.exists():
        print(f"Error: Base image not found at {base_image_path}")
        sys.exit(1)

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load API key and create client
    try:
        api_key = load_api_key()
        client = genai.Client(api_key=api_key)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Load base image
    print(f"Loading base image from: {base_image_path}")
    base_image = Image.open(base_image_path)

    # Generate all combinations
    print(f"\nGenerating {len(EXPRESSIONS) * len(ACTIONS)} character variations...")
    print("=" * 60)

    successful = 0
    failed = 0

    for expression in EXPRESSIONS:
        print(f"\n{expression.upper()}:")
        for action in ACTIONS:
            # Create filename: expression_action.png
            filename = f"{expression}_{action}.png"
            output_path = output_dir / filename

            # Generate the image
            success = generate_character_image(
                client=client,
                base_image=base_image,
                expression=expression,
                action=action,
                output_path=output_path,
            )

            if success:
                successful += 1
            else:
                failed += 1

    # Print summary
    print("\n" + "=" * 60)
    print("\nGeneration complete!")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Total: {successful + failed}")
    print(f"\nGenerated images saved to: {output_dir}")


if __name__ == "__main__":
    main()
