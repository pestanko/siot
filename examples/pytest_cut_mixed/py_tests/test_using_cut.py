from siot import Executable


def test_using_cut_unit_tests(mixed_cut: Executable):
    res = mixed_cut.execute()

    assert res.exit == 0
