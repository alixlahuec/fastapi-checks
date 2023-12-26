from pytest import fixture, mark

from fastapi_checks import models


@fixture
def marked_dep(dependency):
    return models.Mark(marked=dependency)


def test_mark_add_tags(marked_dep):
    assert len(marked_dep.tags) == 0

    marked_dep.add_tags(["tag_1", "tag_2"])
    assert len(marked_dep.tags) == 2

    marked_dep.add_tags(["tag_1", "tag_3"])
    assert len(marked_dep.tags) == 3


@mark.parametrize(
    "tags, include_all_list, expected_result",
    [
        ([], ["tag_1"], False),
        (["tag_1"], ["tag_1"], True),
        (["tag_1"], ["tag_1", "tag_2"], False),
        (["tag_1", "tag_2"], ["tag_1"], True),
    ],
)
def test_mark_predicate_tags_include_all(
    marked_dep, tags, include_all_list, expected_result
):
    marked_dep.add_tags(tags)
    assert (
        marked_dep.predicate(tags_include_all=set(include_all_list)) is expected_result
    )


@mark.parametrize(
    "tags, include_list, expected_result",
    [
        ([], ["tag_1"], False),
        (["tag_1"], ["tag_1"], True),
        (["tag_1"], ["tag_2"], False),
        (["tag_1", "tag_2"], ["tag_2"], True),
        (["tag_1"], ["tag_1", "tag_2"], True),
    ],
)
def test_mark_predicate_tags_include_any(
    marked_dep, tags, include_list, expected_result
):
    marked_dep.add_tags(tags)
    assert marked_dep.predicate(tags_include=set(include_list)) is expected_result


@mark.parametrize(
    "tags, exclude_list, expected_result",
    [
        ([], ["tag_1"], True),
        (["tag_1"], ["tag_1"], False),
        (["tag_1"], ["tag_1", "tag_2"], False),
        (["tag_1"], ["tag_2"], True),
    ],
)
def test_mark_predicate_tags_exclude_all(
    marked_dep, tags, exclude_list, expected_result
):
    marked_dep.add_tags(tags)
    assert marked_dep.predicate(tags_exclude_all=exclude_list) is expected_result


def test_mark_predicate_without_args_returns_true(marked_dep):
    assert marked_dep.predicate() is True


@mark.parametrize(
    "tags, predicate_kwargs, expected_result",
    [
        (
            ["tag_1"],
            dict(
                tags_include=["tag_1"],
                tags_exclude_all=["tag_3"],
                tags_include_all=["tag_1", "tag_2"],
            ),
            False,
        ),
        (
            ["tag_1", "tag_2"],
            dict(
                tags_include=["tag_2"],
                tags_exclude_all=["tag_1"],
            ),
            False,
        ),
    ],
    ids=[
        "tags_include_all is checked first",
        "tags_exclude_all is checked second",
    ],
)
def test_mark_predicate_with_multiple_kwargs(
    marked_dep,
    tags,
    predicate_kwargs,
    expected_result,
):
    marked_dep.add_tags(tags)
    assert marked_dep.predicate(**predicate_kwargs) is expected_result
