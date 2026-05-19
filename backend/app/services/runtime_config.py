from dataclasses import dataclass

from app.core.config import get_settings
from app.schemas.auth import ApiKeyStatus


@dataclass
class RuntimeConfigStore:
    vt_api_key_override: str | None = None

    def current_vt_api_key(self) -> str:
        return self.vt_api_key_override or get_settings().vt_api_key

    def status(self) -> ApiKeyStatus:
        active = self.current_vt_api_key()
        source = 'runtime_override' if self.vt_api_key_override else 'environment'
        return ApiKeyStatus(configured=bool(active), source=source, masked_key=mask_api_key(active))


runtime_config = RuntimeConfigStore()


def mask_api_key(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= 8:
        return '*' * len(value)
    return f"{value[:4]}{'*' * (len(value) - 8)}{value[-4:]}"
