from automations.drive_clean_up_assistant.handler import find_duplicates
from common.storage import FileInfo

def test_find_duplicates():
    a = FileInfo(path="a", size=10, modified_ts=0, sha1="x")
    b = FileInfo(path="b", size=10, modified_ts=0, sha1="x")
    c = FileInfo(path="c", size=9, modified_ts=0, sha1="y")
    groups = find_duplicates([a,b,c])
    assert len(groups) == 1 and {x.path for x in groups[0]} == {"a","b"}
