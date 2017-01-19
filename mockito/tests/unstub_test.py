
from mockito import when, unstub


class Dog(object):
    def waggle(self):
        return 'Unsure'

class TestUntub:
    def testIndependentUnstubbing(self):
        rex = Dog()
        mox = Dog()

        when(rex).waggle().thenReturn('Yup')
        when(mox).waggle().thenReturn('Nope')

        assert rex.waggle() == 'Yup'
        assert mox.waggle() == 'Nope'

        unstub(rex)

        assert rex.waggle() == 'Unsure'
        assert mox.waggle() == 'Nope'

        unstub(mox)

        assert mox.waggle() == 'Unsure'

