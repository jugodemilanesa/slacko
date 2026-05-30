"""State definitions for the guided mode state machine."""


class ChatState:
    START = "START"
    SELECT_MODE = "SELECT_MODE"

    # Guided mode states
    INPUT_ENUNCIADO = "INPUT_ENUNCIADO"
    CLASSIFY_SCENARIO = "CLASSIFY_SCENARIO"
    DEFINE_VARIABLES = "DEFINE_VARIABLES"
    DEFINE_OBJECTIVE = "DEFINE_OBJECTIVE"
    BUILD_CONSTRAINTS = "BUILD_CONSTRAINTS"
    VALIDATE_MODEL = "VALIDATE_MODEL"
    CONVERT_FORMS = "CONVERT_FORMS"
    SOLVE_AND_GRAPH = "SOLVE_AND_GRAPH"
    INTERPRET = "INTERPRET"

    # Free mode states
    INPUT_MODEL = "INPUT_MODEL"
    PARSE_AND_VALIDATE = "PARSE_AND_VALIDATE"

    ALL_STATES = [
        START,
        SELECT_MODE,
        INPUT_ENUNCIADO,
        CLASSIFY_SCENARIO,
        DEFINE_VARIABLES,
        DEFINE_OBJECTIVE,
        BUILD_CONSTRAINTS,
        VALIDATE_MODEL,
        CONVERT_FORMS,
        SOLVE_AND_GRAPH,
        INTERPRET,
        INPUT_MODEL,
        PARSE_AND_VALIDATE,
    ]

    GUIDED_FLOW = [
        INPUT_ENUNCIADO,
        CLASSIFY_SCENARIO,
        DEFINE_VARIABLES,
        DEFINE_OBJECTIVE,
        BUILD_CONSTRAINTS,
        VALIDATE_MODEL,
        CONVERT_FORMS,
        SOLVE_AND_GRAPH,
        INTERPRET,
    ]

    FREE_FLOW = [
        INPUT_MODEL,
        PARSE_AND_VALIDATE,
        SOLVE_AND_GRAPH,
        INTERPRET,
    ]


def next_state(current: str) -> str | None:
    """Return the next state in the guided flow, or ``None`` if already at the end."""
    try:
        idx = ChatState.GUIDED_FLOW.index(current)
        if idx + 1 < len(ChatState.GUIDED_FLOW):
            return ChatState.GUIDED_FLOW[idx + 1]
        return None
    except ValueError:
        return None


def previous_state(current: str) -> str | None:
    """Return the previous state in the guided flow, or ``None`` if at the start."""
    try:
        idx = ChatState.GUIDED_FLOW.index(current)
        if idx - 1 >= 0:
            return ChatState.GUIDED_FLOW[idx - 1]
        return None
    except ValueError:
        return None
