import reprmeta

def test_get_metadata_runs():
    assert isinstance(reprmeta.get_metadata(), dict)
