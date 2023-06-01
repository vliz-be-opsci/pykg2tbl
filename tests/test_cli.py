from util4tests import run_single_test

from pykg2tbl.__main__ import main as kg2tbl


def test_basic():
    arg1 = "tests/sources/01-persons-shape.ttl"
    arg2 = "tests/sources/02-person.ttl"
    output = "/tmp/test_kg2tbl_vliz.csv"

    kg2tbl(f"-s {arg1} {arg2} -o {output} -t all.sparql".split(" "))
    pass


if __name__ == "__main__":
    run_single_test(__file__)
