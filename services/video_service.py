"""
Video Generation Module using Replicate API
"""

import replicate


def generate_video(description: str, quality: str = "720p") -> str:
    """
    Generate video from text description using Replicate API

    Args:
        description: Text description of the video to generate
        quality: Video quality (480p, 720p, 1080p, 4k)

    Returns:
        URL of the generated video
    """
    quality_map = {
        "480p": "854x480",
        "720p": "1280x720",
        "1080p": "1920x1080",
        "4k": "3840x2160",
    }

    resolution = quality_map.get(quality, "1280x720")
    width, height = map(int, resolution.split("x"))

    models = [
        {
            "id": "anotherjesse/zeroscope-v2-xl:9f747673945c62801b13b84701c783929c0ee784e4748ec062204894dda1a351",
            "params": {
                "num_frames": 24,
                "num_inference_steps": 50,
                "guidance_scale": 17.5,
                "fps": 10,
            },
        },
        {
            "id": "damo-vilab/text-to-video-ms-1.7b:495d409b30c6a850125746b4020a59a9301886cb4f183724c9c64609827052dc",
            "params": {"num_frames": 16, "num_inference_steps": 30, "fps": 8},
        },
    ]

    import time

    last_error = None

    for model in models:
        for attempt in range(2):
            try:
                print(
                    f"Attempting video generation with model {model['id'][:20]}... (Attempt {attempt+1})"
                )

                input_params = model["params"].copy()
                input_params["prompt"] = description

                if "zeroscope" in model["id"]:
                    input_params["width"] = width
                    input_params["height"] = height

                output = replicate.run(model["id"], input=input_params)

                if isinstance(output, list) and len(output) > 0:
                    return output[0]
                if isinstance(output, str):
                    return output

            except Exception as e:
                print(f"Error with model {model['id'][:20]}: {str(e)}")
                last_error = e
                time.sleep(2)
                continue

    raise Exception(
        f"Video generation failed after multiple attempts. Last error: {str(last_error)}"
    )


def download_video(video_url: str, save_path: str) -> str:
    """
    Download video from URL to local path
    """
    import requests

    try:
        response = requests.get(video_url, stream=True, timeout=300)
        response.raise_for_status()

        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return save_path
    except Exception as e:
        raise Exception(f"Video download failed: {str(e)}")

