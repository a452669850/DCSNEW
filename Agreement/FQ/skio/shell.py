from Agreement.FQ.skio import skio
from Agreement.FQ.skio.worker.state import SkWorkerState
from pathlib import Path


if __name__ == '__main__':
    # path = "E:\workspace\dcsProj\demo"
    path = Path('~/workspace/福清测试工程/demo').expanduser()
    skio.setup(path)

    # st = SkWorkerState()
    # st.setup(path)
    skio.write('XRCS180MP', value='80.0%FP(TX)')
    skio.write('5RCS181MP', value='95.0%FP(CH1)')
    skio.write('XRCS181MP', value='80.0%FP(CH1)')

    print(skio.read('5RPA100JA_UV', need_time=True))


