from pathlib import Path

from RealtimeDB.manage import SkIO
from RealtimeDB.view.utils.iomapping import IOMapping


path = Path(__file__).absolute().parent.parent.joinpath('static/demo')

skio = SkIO()
# skio.start()
# print(skio.read('PXI-6528/CH1'))
iomapping = IOMapping(path)