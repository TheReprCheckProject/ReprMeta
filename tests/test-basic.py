import reprmeta

def test_metadata_runs():
    assert isinstance(reprmeta.metadata(), dict)
