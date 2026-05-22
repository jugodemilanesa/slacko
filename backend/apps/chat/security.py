"""Pre-filter de prompt injection.

Detecta los patrones más obvios de intento de manipulación del system prompt
antes de gastar un hop de LLM. La filosofía:

* **Conservador**: preferimos pasar un mensaje sospechoso al LLM (que ya
  tiene un system prompt endurecido) antes que bloquear a un alumno legítimo.
  El SYSTEM_PROMPT de ``apps.orchestrator.orchestrator`` ya tiene una sección
  ``DEFENSA ANTE PROMPT INJECTION`` — este filtro es una primera línea, no
  la única.
* **High signal**: solo bloqueamos patrones donde la intención maliciosa es
  inequívoca (tokens de protocolo de chat templates, frases textualmente
  diseñadas para jailbreak, etc.). Mensajes que "podrían" ser injection pero
  también podrían ser legítimos (ej. "explicame qué hace el system prompt en
  inteligencia artificial") los dejamos pasar al LLM.
* **Loggeable**: cada bloqueo registra el patrón que matchea + un fragmento
  del input, para iterar sobre los casos reales que aparezcan.

Si querés agregar un patrón nuevo, verificalo contra los tests en
``apps/chat/tests/test_security.py`` para no romper falsos negativos.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


# ──────────────────────────────────────────────────────────────────────────
# Patrones de injection. Cada uno es una tupla (label, compiled_regex).
# ──────────────────────────────────────────────────────────────────────────

# Tokens de chat-template usados en muchos prompts maliciosos para simular
# turnos del rol "system" o "assistant". Si el usuario escribe esto, casi
# seguro está intentando inyectar.
_TEMPLATE_TOKENS = re.compile(
    r"<\|(?:im_start|im_end|endoftext|start_header_id|end_header_id|eot_id)\|>",
    re.IGNORECASE,
)

# "ignore [the|all|your] [previous|above|prior] instructions" + variantes ES.
_IGNORE_INSTRUCTIONS_EN = re.compile(
    r"\b(?:ignore|disregard|forget)\s+(?:all\s+|the\s+|your\s+|any\s+|every\s+)*"
    r"(?:previous|prior|above|all)\s+(?:instructions?|rules?|prompts?|directives?)",
    re.IGNORECASE,
)
_IGNORE_INSTRUCTIONS_ES = re.compile(
    r"\b(?:ignor[áa]|olvid[áa]|desconoc[ée])\s+(?:todas?\s+|tus\s+|las\s+|el\s+|los\s+)*"
    r"(?:anteriores?|previas?|reglas?|instrucciones?|prompts?|directivas?)",
    re.IGNORECASE,
)

# Pedidos explícitos de "revelar/mostrar/imprimir el system prompt".
_REVEAL_PROMPT_EN = re.compile(
    r"\b(?:reveal|show|print|output|display|expose|leak)\s+(?:me\s+)?(?:your|the)\s+"
    r"(?:system\s+|hidden\s+|original\s+|initial\s+)?(?:prompt|instructions|rules)\b",
    re.IGNORECASE,
)
_REVEAL_PROMPT_ES = re.compile(
    r"\b(?:rev[ée]l(?:ame|ar)?|mostr[áa]me|impr[ií]m(?:ir|íme))\s+(?:tu|el|tus|las)\s+"
    r"(?:prompt|instrucciones|reglas|sistema|configuraci[óo]n)",
    re.IGNORECASE,
)

# Modo developer / jailbreak / DAN — términos de la cultura de jailbreak.
_JAILBREAK = re.compile(
    r"\b(?:developer\s+mode|jailbreak(?:ed)?|do\s+anything\s+now|\bdan\s+mode)\b",
    re.IGNORECASE,
)

# Roleplay impuesto explícito: "from now on you are X". Excluimos cuando
# el rol que asigna está claramente alineado con PL (por las dudas, raro).
# El verbo "actuar" en español tiene 3 formas válidas (actua/actúa/actuá tú/usted/vos)
# por eso aceptamos las tres combinaciones de tildes.
_FORCE_ROLE = re.compile(
    r"\b(?:from\s+now\s+on|de\s+ahora\s+en\s+m[áa]s|a\s+partir\s+de\s+ahora)\s+"
    r"(?:you\s+are|sos|act[uú][aá]\s+como|pretend|comp[óo]rtate|finge\s+ser)",
    re.IGNORECASE,
)

# Línea estilo system-prompt incrustada por el usuario.
# Buscamos un "system:" o "[system]" o "###system" al principio de una línea,
# que es la forma en que la gente intenta forzar otra instrucción de sistema.
_FAKE_SYSTEM_LINE = re.compile(
    r"(?:^|\n)\s*(?:#{1,4}\s*)?(?:\[\s*)?system\s*\]?\s*:",
    re.IGNORECASE,
)


_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("template_tokens", _TEMPLATE_TOKENS),
    ("ignore_instructions_en", _IGNORE_INSTRUCTIONS_EN),
    ("ignore_instructions_es", _IGNORE_INSTRUCTIONS_ES),
    ("reveal_prompt_en", _REVEAL_PROMPT_EN),
    ("reveal_prompt_es", _REVEAL_PROMPT_ES),
    ("jailbreak", _JAILBREAK),
    ("force_role", _FORCE_ROLE),
    ("fake_system_line", _FAKE_SYSTEM_LINE),
]


@dataclass(frozen=True)
class InjectionVerdict:
    """Resultado de evaluar un texto contra el filtro."""

    blocked: bool
    pattern: Optional[str] = None
    excerpt: Optional[str] = None  # fragmento del input que matcheó, para logging


def evaluate(text: str) -> InjectionVerdict:
    """Devuelve el primer patrón que matchea, o ``allowed`` si pasa todos."""

    if not text:
        return InjectionVerdict(blocked=False)

    for label, pat in _PATTERNS:
        m = pat.search(text)
        if m:
            # Slice around the match for logging — limit to 120 chars.
            start = max(0, m.start() - 24)
            end = min(len(text), m.end() + 24)
            excerpt = text[start:end].replace("\n", " ").strip()
            if len(excerpt) > 120:
                excerpt = excerpt[:117] + "..."
            return InjectionVerdict(blocked=True, pattern=label, excerpt=excerpt)

    return InjectionVerdict(blocked=False)
