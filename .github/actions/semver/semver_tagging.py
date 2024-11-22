import os
import json
from dataclasses import dataclass
from datetime import datetime, UTC
from enum import StrEnum, auto

from github import Github, Auth, Repository

REPO_NAME = "Relativity74205/murkelhausen_app_v2"


@dataclass
class Tag:
    major: int
    minor: int
    patch: int

    @classmethod
    def from_tag_name(cls, tag_name: str) -> "Tag":
        major, minor, patch = tag_name.split(".")
        return cls(int(major), int(minor), int(patch))

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"

    def __eq__(self, other):
        if not isinstance(other, Tag):
            return NotImplemented
        return (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
        )

    def __lt__(self, other):
        if not isinstance(other, Tag):
            return NotImplemented
        if self.major < other.major:
            return True
        elif self.major == other.major:
            if self.minor < other.minor:
                return True
            elif self.minor == other.minor:
                if self.patch < other.patch:
                    return True
        return False

    @staticmethod
    def as_string(major: int, minor: int, patch: int):
        return f"{major}.{minor}.{patch}"

    def return_next_major(self) -> "Tag":
        return Tag(self.major + 1, 0, 0)

    def return_next_minor(self) -> "Tag":
        return Tag(self.major, self.minor + 1, 0)

    def return_next_patch(self) -> "Tag":
        return Tag(self.major, self.minor, self.patch + 1)


class UpgradeType(StrEnum):
    MAJOR = auto()
    MINOR = auto()
    PATCH = auto()
    NONE = auto()


def get_github_repo() -> Repository:
    github_token = os.environ["GITHUB_TOKEN"]
    auth = Auth.Token(github_token)

    g = Github(auth=auth)

    return g.get_repo(REPO_NAME)


def get_last_tag(repo: Repository) -> tuple[Tag | None, datetime | None]:
    tags = repo.get_tags()
    try:
        last_tag = sorted(tags, key=lambda x: Tag.from_tag_name(x.name), reverse=True)[
            0
        ]
        return Tag.from_tag_name(last_tag.name), last_tag.commit.commit.author.date
    except IndexError:
        return None, None


def get_commit_messages_since_tag(
    repo: Repository, last_tag_datetime: datetime
) -> list[str]:
    if last_tag_datetime is None:
        commits_since_tag = repo.get_commits()
        last_tag_datetime = datetime.fromtimestamp(0, tz=UTC)
    else:
        commits_since_tag = repo.get_commits(since=last_tag_datetime)
    return [
        commit.commit.message
        for commit in commits_since_tag
        if commit.commit.author.date > last_tag_datetime
    ]


def get_conventional_commits_prefix(commit_message: str) -> str | None:
    try:
        return commit_message.split(":")[0].strip()
    except IndexError:
        return None


def is_breaking_change(commit_message: str) -> bool:
    return "BREAKING" in commit_message


def get_upgrade_type(commit_messages: list[str]) -> UpgradeType:
    for commit_message in commit_messages:
        if is_breaking_change(commit_message):
            return UpgradeType.MAJOR

    for commit_message in commit_messages:
        if get_conventional_commits_prefix(commit_message) == "feat":
            return UpgradeType.MINOR

    for commit_message in commit_messages:
        if get_conventional_commits_prefix(commit_message) == "fix":
            return UpgradeType.PATCH

    return UpgradeType.NONE


def calculate_next_tag(commit_messages: list[str], last_tag: Tag) -> Tag:
    if last_tag is None:
        return Tag(0, 0, 1)

    upgrade_type = get_upgrade_type(commit_messages)

    match upgrade_type:
        case UpgradeType.MAJOR:
            return last_tag.return_next_major()
        case UpgradeType.MINOR:
            return last_tag.return_next_minor()
        case UpgradeType.PATCH:
            return last_tag.return_next_patch()
        case _:
            return last_tag


def main():
    print("Start.")
    github_repo = get_github_repo()
    last_tag, last_tag_datetime = get_last_tag(github_repo)
    print(f"last_tag={str(last_tag)} with {last_tag_datetime=}")
    commit_messages = get_commit_messages_since_tag(github_repo, last_tag_datetime)

    next_tag = calculate_next_tag(commit_messages, last_tag)
    print(f"next_tag={str(next_tag)}")
    if next_tag == last_tag:
        print("No new tag needed.")
        result_dict = {
            "NEXT_TAG": "",
            "CHANGELOG": "",
        }
    else:
        result_dict = {
            "NEXT_TAG": str(next_tag),
            "CHANGELOG": "\n".join(commit_messages),
        }
    print(f"{result_dict=}")

    with open("semver_result.json", "w") as f:
        json.dump(result_dict, f, indent=4)


if __name__ == "__main__":
    main()
