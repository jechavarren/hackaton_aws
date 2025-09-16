from langchain_core.tools import tool
from get_user_data import get_customer_full_info
from typing import Annotated, List


@tool
def multiply_by_max(
    a: Annotated[int, "scale factor"],
    b: Annotated[List[int], "list of ints over which to take maximum"],
) -> int:
    """Multiply a by the maximum of b."""
    return a * max(b)


# print(multiply_by_max.args_schema.model_json_schema())

@tool
def get_customer_info(
    user: Annotated[str, "User complete name, Name+ Surname, with the first letter of name and surname being in capital letters"],
) -> str:
    """Get the bank transaction data from that user"""

    return get_customer_full_info(customer_name=user)

@tool
def get_customer_current_products(
    user: Annotated[str, "User complete name, Name+ Surname, with the first letter of name and surname being in capital letters"],
) -> str:
    """Get the currently used financial products by the customer"""

    result=  get_customer_full_info(customer_name=user)

    return {
        "Product_Usage": result["Product_Usage"],
    }