"""
Escape curly braces in dynamic text so {xx} is not interpreted as a variable placeholder.

Used when embedding user/model content into templates that use {variable} substitution
(e.g. ADK instruction inject_session_state). If the runtime is changed later, remove
the decorator or calls and braces no longer need escaping.
"""

import functools
import inspect


def sanitize_braces(text: str) -> str:
    """Escape `{` and `}` in text so they are not treated as variable placeholders.

    Use for any dynamic content (user input, model output, plan text, etc.) before
    inserting into a template that does {name} substitution. Empty/None returns as-is.
    """
    if not text:
        return text
    return text.replace('\\', '\\\\').replace('{', '\\{').replace('}', '\\}')


def with_sanitized_braces(*param_names: str):
    """Decorator: sanitize the listed string parameters before calling the function.

    Use on functions that build instruction/template strings from dynamic args.
    If you stop using a runtime that interprets {var}, remove this decorator and
    no other logic changes are needed.
    """
    param_set = set(param_names)

    def deco(f):
        sig = inspect.signature(f)

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            for name in param_set:
                if name in bound.arguments and isinstance(bound.arguments[name], str):
                    bound.arguments[name] = sanitize_braces(bound.arguments[name])
            args_list = []
            kwargs_dict = {}
            for name in sig.parameters:
                p = sig.parameters[name]
                val = bound.arguments.get(name)
                if p.kind == inspect.Parameter.VAR_POSITIONAL:
                    args_list.extend(val)
                elif p.kind == inspect.Parameter.VAR_KEYWORD:
                    kwargs_dict.update(val)
                elif p.kind in (
                    inspect.Parameter.POSITIONAL_ONLY,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                ):
                    args_list.append(val)
                else:
                    kwargs_dict[name] = val
            return f(*args_list, **kwargs_dict)

        return wrapper

    return deco
