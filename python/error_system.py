from dataclasses import dataclass
from typing import Any

from utils import load_config


@dataclass(frozen=True)
class ErrorSpec:
    code: str
    title: str
    hint: str


ERROR_SPECS: dict[str, ErrorSpec] = {
    "SG-0001": ErrorSpec("SG-0001", "Configuracion invalida", "Revisa config.json y docs/CONFIG.md"),
    "SG-0002": ErrorSpec("SG-0002", "Dependencia faltante", "Instala dependencias con scripts/install.bat"),
    "SG-0003": ErrorSpec("SG-0003", "Operacion de red fallida", "Verifica conexion y vuelve a intentar"),
    "SG-0004": ErrorSpec("SG-0004", "Operacion Git fallida", "Revisa docs/UPDATE_SYSTEM.md"),
    "SG-0005": ErrorSpec("SG-0005", "Operacion de plugin fallida", "Revisa plugins/ y docs/PLUGINS.md"),
    "SG-9999": ErrorSpec("SG-9999", "Error no controlado", "Revisa server.log y docs/ERROR_CODES.md"),
}


class AppError(RuntimeError):
    def __init__(self, code: str, message: str, details: str | None = None):
        self.code = code if code in ERROR_SPECS else "SG-9999"
        self.message = message
        self.details = details
        super().__init__(self.format_message())

    def format_message(self) -> str:
        spec = ERROR_SPECS.get(self.code, ERROR_SPECS["SG-9999"])
        parts = [f"[{self.code}] {spec.title}: {self.message}", f"Sugerencia: {spec.hint}"]
        repo = _docs_repo_url()
        if repo:
            parts.append(f"Referencia: {repo}/blob/main/docs/ERROR_CODES.md#{self.code.lower()}")
        if self.details:
            parts.append(f"Detalles: {self.details}")
        return " | ".join(parts)


def raise_if_false(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise AppError(code, message)


def map_exception_to_app_error(ex: Exception) -> AppError:
    text = str(ex).lower()
    if "npm" in text or "node" in text or "python" in text:
        return AppError("SG-0002", str(ex))
    if "git" in text:
        return AppError("SG-0004", str(ex))
    if "http" in text or "network" in text or "timeout" in text:
        return AppError("SG-0003", str(ex))
    return AppError("SG-9999", str(ex))


def explain_error(code: str) -> str:
    spec = ERROR_SPECS.get(code, ERROR_SPECS["SG-9999"])
    repo = _docs_repo_url()
    link = ""
    if repo:
        link = f" | Docs: {repo}/blob/main/docs/ERROR_CODES.md#{spec.code.lower()}"
    return f"[{spec.code}] {spec.title} | {spec.hint}{link}"


def _docs_repo_url() -> str:
    cfg: dict[str, Any] = load_config()
    repo = str(cfg.get("support", {}).get("repoUrl", "")).rstrip("/")
    if not repo or "owner/servergo" in repo.lower():
        return "https://github.com/BluePandaOpn/ServerGo"
    return repo

