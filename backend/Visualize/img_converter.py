import io
import base64
import matplotlib.pyplot as plt

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format = 'png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return image_base64