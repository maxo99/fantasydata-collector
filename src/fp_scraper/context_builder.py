import logging
from typing import Any
from my_fake_useragent import UserAgent as FakeUserAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# user_agent_list = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
# ]
 

def _user_agent() -> str:
    # return random.choice(user_agent_list)
    return FakeUserAgent(family="chrome").random()


def get_context_args(record_mode: bool) -> dict[str, Any]:
    args: dict[str, Any] = dict(user_agent=_user_agent())
    if record_mode:
        args["record_video_dir"] = "videos/"
        args["record_video_size"] = {"width": 640, "height": 480}
    return args
