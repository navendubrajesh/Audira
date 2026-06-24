"""Provider factory — routes model_id to the correct inference backend."""

from resonode_core.inference.provider import HttpGpuProvider, MockGpuProvider

TRIBE_V2_MODEL_IDS = {"tribe-v2", "facebook/tribev2", "tribe-v2-stub"}


def build_provider(
    *,
    model_id: str = "tribe-v2-stub",
    inference_base_url: str = "",
    inference_api_key: str = "",
) -> HttpGpuProvider | MockGpuProvider:
    """
    TRIBE v2 always runs on the decoupled GPU tier (never inside API/worker containers).

    - model_id in TRIBE_V2_MODEL_IDS + INFERENCE_BASE_URL set → HttpGpuProvider → GPU service
    - model_id in TRIBE_V2_MODEL_IDS + no URL → MockGpuProvider (dev stub with tribe-v2 label)
    - other models → HttpGpuProvider if URL set, else MockGpuProvider
    """
    use_http = bool(inference_base_url)
    if model_id in TRIBE_V2_MODEL_IDS:
        if use_http:
            return HttpGpuProvider(inference_base_url, inference_api_key)
        return MockGpuProvider(model_label="tribe-v2-stub")
    if use_http:
        return HttpGpuProvider(inference_base_url, inference_api_key)
    return MockGpuProvider()
