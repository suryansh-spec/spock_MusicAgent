class ValidationError(Exception):
    pass


def validate_action(llm_output: dict, schema: dict) -> dict:
    # 1. Action check
    if llm_output.get("action") != schema["name"]:
        raise ValidationError("Unauthorized action")

    params = llm_output.get("parameters", {})
    if not isinstance(params, dict):
        raise ValidationError("Parameters must be an object")

    validated = {}

    # 2. Validate each schema-defined parameter independently
    for name, rules in schema["parameters"].items():

        # ---- Parameter not provided ----
        if name not in params:
            if name in schema.get("required", []):
                raise ValidationError(f"Missing required parameter: {name}")
            continue

        value = params[name]  # <-- value is guaranteed to exist from here down

        # ---- Type check ----
        if not isinstance(value, rules["type"]):
            raise ValidationError(f"{name} has wrong type")

        # ---- Enum / allowed values ----
        if "allowed" in rules and value not in rules["allowed"]:
            raise ValidationError(f"{name} not allowed")

        # ---- String constraints ----
        if rules["type"] is str:
            if "min_length" in rules:
                if not (rules["min_length"] <= len(value) <= rules["max_length"]):
                    raise ValidationError(f"{name} length invalid")

        # ---- Integer constraints ----
        if rules["type"] is int:
            if "min" in rules and value < rules["min"]:
                raise ValidationError(f"{name} below minimum")
            if "max" in rules and value > rules["max"]:
                raise ValidationError(f"{name} above maximum")

        validated[name] = value

    return validated
