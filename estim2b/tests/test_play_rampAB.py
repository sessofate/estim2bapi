import pytest
from play import rampAB
from estim2b import Estim

@pytest.mark.parametrize("slA,elA,slB,elB,dur,mode,power,block", [(0,15,0,100,2,None,"L",False)])
def test_rampAB(slA, elA, slB, elB, dur, mode, power, block):
    e2b = Estim(recv_responses=True, dryrun=True, verbose=2)
    e2b.start()
    print(e2b.get_status())

    rampAB(e2b, slA, elA, slB, elB, dur, mode=mode, power=power, block=block)
    e2b.stop()

