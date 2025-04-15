from typing import Any, Union
from typing import get_origin, get_args



def resolve_type(field_type: Any):
    """Resolves `Optional` and `Union` types to their underlying type if possible.
    
    his function is useful when working with type annotations that can include multiple types,
    especially Optional[T], which is essentially for Union[T, None]. When converting data
    (such as from strings or dictionaries) to strongly typed fields, you often need to know 
    the base type for proper casting or instantiation.

    Examples:
        Optional[int] -> int
        Union[str, None] -> str
        int -> int (unchanged)
    
    Returns:
        resolved (Any): The resolved underlying type, or the original type if no resolution is needed.
    """
    origin = get_origin(field_type)
    if origin is Union:
        args = get_args(field_type)
        non_none_args = [arg for arg in args if arg is not type(None)]
        if len(non_none_args) == 1:
            return non_none_args[0]

    return field_type