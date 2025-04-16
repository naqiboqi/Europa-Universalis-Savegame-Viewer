from __future__ import annotations


import io
import matplotlib.pyplot as plt

from PIL import Image
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..models import EUTradeNode


def draw_trade_value_pie_bytes(trade_node: EUTradeNode, size: tuple[int, int]=(150, 150)):
    """Generates a pie chart that shows the trade value distribution
    in the specified trade node. Returns the chart as bytes.
    
    Args:
        trade_node (EUTradeNode): The trade node to draw the chart for.
    
    Returns:
        bytes: PNG image data of the pie chart showing retained vs outgoing trade value.
    """
    sizes = [trade_node.local_trade_value, trade_node.outgoing_trade_value]
    chart_colors = [
    (102/255, 187/255, 106/255),
    (239/255, 83/255, 80/255) 
]

    fig, ax = plt.subplots()
    ax.pie(
        sizes,
        labels=None,
        autopct='%1.1f%%',
        startangle=90,
        counterclock=False,
        colors=chart_colors)

    ax.axis("equal")

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight", dpi=150, transparent=True)
    plt.close(fig)

    buffer.seek(0)

    pil_img = Image.open(buffer)
    pil_img = pil_img.resize(size, Image.Resampling.LANCZOS)

    resized_buffer = io.BytesIO()
    pil_img.save(resized_buffer, format='PNG')
    resized_buffer.seek(0)

    return resized_buffer.getvalue() 