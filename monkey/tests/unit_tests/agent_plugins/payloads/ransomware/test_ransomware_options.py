import pytest
from agent_plugins.payloads.ransomware.src.ransomware_options import (
    EncryptionBehavior,
    RansomwareOptions,
)

ENCRYPTION_BEHAVIOR_DICT = {
    "file_extension": ".encrypted",
    "linux_target_dir": "/tmp",
    "windows_target_dir": "C:/temp/",
}

ENCRYPTION_BEHAVIOR_OBJECT = EncryptionBehavior(
    file_extension=".encrypted",
    linux_target_dir="/tmp",
    windows_target_dir="C:/temp/",
)

RANSOMWARE_OPTIONS_DICT = {"encryption": ENCRYPTION_BEHAVIOR_OBJECT, "other_behaviors": {}}

RANSOMWARE_OPTIONS_OBJECT = RansomwareOptions(
    encryption=ENCRYPTION_BEHAVIOR_OBJECT,
)


def test_ransomware_options__serialization():
    assert RANSOMWARE_OPTIONS_OBJECT.dict(simplify=True) == RANSOMWARE_OPTIONS_DICT


def test_ransomware_options__full_serialization():
    assert (
        RansomwareOptions(**RANSOMWARE_OPTIONS_OBJECT.dict(simplify=True))
        == RANSOMWARE_OPTIONS_OBJECT
    )


def test_ransomware_options__deserialization():
    assert RansomwareOptions(**RANSOMWARE_OPTIONS_DICT) == RANSOMWARE_OPTIONS_OBJECT


def test_ransomware_options__default():
    ransomware_options = RansomwareOptions()

    assert ransomware_options.encryption.file_extension == ".m0nk3y"
    assert ransomware_options.encryption.linux_target_dir == ""
    assert ransomware_options.encryption.windows_target_dir == ""
    assert ransomware_options.other_behaviors == {}


@pytest.mark.parametrize(
    "file_extension",
    [" ", "..", "123", "xyz", ". .x", "x.", ".x\\y", ".x/", ".x/y", ".?", "!", "/", "~"],
)
def test_ransomware_options__invalid_file_extension(file_extension):
    with pytest.raises(ValueError):
        RansomwareOptions(encryption=EncryptionBehavior(file_extension=file_extension))


@pytest.mark.parametrize(
    "windows_target_dir", ["C::", ":/temp", "\\", "...", "~", "/home/user", "-abc", "01234", " "]
)
def test_ransomware_options__invalid_windows_target_dir(windows_target_dir):
    with pytest.raises(ValueError):
        RansomwareOptions(encryption=EncryptionBehavior(windows_target_dir=windows_target_dir))


@pytest.mark.parametrize(
    "linux_target_dir",
    ["C:\hello", "\\\\", "C::", ":/temp", "\\", "...", "-abc", "01234", " ", "a~b"],  # noqa: W605
)
def test_ransomware_options__invalid_linux_target_dir(linux_target_dir):
    with pytest.raises(ValueError):
        RansomwareOptions(encryption=EncryptionBehavior(linux_target_dir=linux_target_dir))
