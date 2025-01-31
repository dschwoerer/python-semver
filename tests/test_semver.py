import pytest  # noqa

from semver import Version


@pytest.mark.parametrize(
    "string,expected", [("rc", "rc"), ("rc.1", "rc.2"), ("2x", "3x")]
)
def test_should_private_increment_string(string, expected):
    assert Version._increment_string(string) == expected


@pytest.mark.parametrize(
    "ver",
    [
        {"major": -1},
        {"major": 1, "minor": -2},
        {"major": 1, "minor": 2, "patch": -3},
        {"major": 1, "minor": -2, "patch": 3},
    ],
)
def test_should_not_allow_negative_numbers(ver):
    with pytest.raises(ValueError, match=".* is negative. .*"):
        Version(**ver)


def test_should_versioninfo_to_dict(version):
    resultdict = version.to_dict()
    assert isinstance(resultdict, dict), "Got type from to_dict"
    assert list(resultdict.keys()) == ["major", "minor", "patch", "prerelease", "build"]
    assert tuple(resultdict.values()) == tuple(version)


def test_should_versioninfo_to_tuple(version):
    result = version.to_tuple()
    assert isinstance(result, tuple), "Got type from to_dict"
    assert len(result) == 5, "Different length from to_tuple()"


def test_version_info_should_be_iterable(version):
    assert tuple(version) == (
        version.major,
        version.minor,
        version.patch,
        version.prerelease,
        version.build,
    )


def test_should_be_able_to_use_strings_as_major_minor_patch():
    v = Version("1", "2", "3")
    assert isinstance(v.major, int)
    assert isinstance(v.minor, int)
    assert isinstance(v.patch, int)
    assert v.prerelease is None
    assert v.build is None
    assert Version("1", "2", "3") == Version(1, 2, 3)


def test_using_non_numeric_string_as_major_minor_patch_throws():
    with pytest.raises(ValueError):
        Version("a")
    with pytest.raises(ValueError):
        Version(1, "a")
    with pytest.raises(ValueError):
        Version(1, 2, "a")


def test_should_be_able_to_use_integers_as_prerelease_build():
    v = Version(1, 2, 3, 4, 5)
    assert isinstance(v.prerelease, str)
    assert isinstance(v.build, str)
    assert Version(1, 2, 3, 4, 5) == Version(1, 2, 3, "4", "5")


def test_should_versioninfo_isvalid():
    assert Version.is_valid("1.0.0") is True
    assert Version.is_valid("foo") is False


def test_versioninfo_compare_should_raise_when_passed_invalid_value():
    with pytest.raises(TypeError):
        Version(1, 2, 3).compare(4)


@pytest.mark.parametrize(
    "old, new",
    [
        ((1, 2, 3), (1, 2, 3)),
        ((1, 2, 3), (1, 2, 4)),
        ((1, 2, 4), (1, 2, 3)),
        ((1, 2, 3, "rc.0"), (1, 2, 4, "rc.0")),
        ((0, 1, 0), (0, 1, 0)),
    ],
)
def test_should_succeed_compatible_match(old, new):
    old = Version(*old)
    new = Version(*new)
    assert old.is_compatible(new)


@pytest.mark.parametrize(
    "old, new",
    [
        ((1, 1, 0), (1, 0, 0)),
        ((2, 0, 0), (1, 5, 0)),
        ((1, 2, 3, "rc.1"), (1, 2, 3, "rc.0")),
        ((1, 2, 3, "rc.1"), (1, 2, 4, "rc.0")),
        ((0, 1, 0), (0, 1, 1)),
        ((1, 0, 0), (1, 0, 0, "rc1")),
        ((1, 0, 0, "rc1"), (1, 0, 0)),
    ],
)
def test_should_fail_compatible_match(old, new):
    old = Version(*old)
    new = Version(*new)
    assert not old.is_compatible(new)


@pytest.mark.parametrize(
    "wrongtype",
    [
        "wrongtype",
        dict(a=2),
        list(),
    ],
)
def test_should_fail_with_incompatible_type_for_compatible_match(wrongtype):
    with pytest.raises(TypeError, match="Expected a Version type .*"):
        v = Version(1, 2, 3)
        v.is_compatible(wrongtype)


def test_should_succeed_with_compatible_subclass_for_is_compatible():
    class CustomVersion(Version):
        ...

    assert CustomVersion(1, 0, 0).is_compatible(Version(1, 0, 0))
