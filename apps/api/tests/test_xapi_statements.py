"""Reading a statement, without believing the sender more than necessary.

These tests stay off the database on purpose: what they pin is what the platform
agrees to keep of an incoming statement, and that decision is made before
anything is written.
"""

from __future__ import annotations

import uuid

import pytest

from app.core.exceptions import ValidationException
from app.models.xapi import MAX_STATEMENT_BYTES, VERB_ANSWERED, VERB_COMPLETED
from app.xapi import statements

KEY = "0" * 64


def statement(**overrides: object) -> dict[str, object]:
    body: dict[str, object] = {
        "id": str(uuid.uuid4()),
        "actor": {"objectType": "Agent", "name": "Léa Dupont"},
        "verb": {"id": VERB_ANSWERED},
        "object": {"id": "http://content.local/h5p/1?subContentId=q1"},
        "result": {"success": True, "response": "vrai"},
        "timestamp": "2026-08-15T10:00:00Z",
    }
    body.update(overrides)
    return body


class TestTheActorIsNeverTheOneClaimed:
    def test_the_claimed_actor_is_replaced(self) -> None:
        """A browser must not be able to write a real name into the database."""
        parsed = statements.parse(statement(), KEY)

        assert parsed.statement["actor"] == statements.pseudonymous_actor(KEY)

    def test_no_trace_of_the_claimed_name_is_kept(self) -> None:
        parsed = statements.parse(statement(), KEY)

        assert "Léa Dupont" not in str(parsed.statement)

    def test_a_statement_without_an_actor_gets_one_anyway(self) -> None:
        body = statement()
        del body["actor"]

        parsed = statements.parse(body, KEY)

        assert parsed.statement["actor"]["account"]["name"] == KEY  # type: ignore[index]

    def test_the_key_depends_on_the_child(self) -> None:
        first = statements.actor_key(uuid.uuid4())
        second = statements.actor_key(uuid.uuid4())

        assert first != second

    def test_the_key_is_stable_for_one_child(self) -> None:
        child_id = uuid.uuid4()

        assert statements.actor_key(child_id) == statements.actor_key(child_id)

    def test_the_key_is_not_the_child_identifier(self) -> None:
        """A database dump must not read as a list of children."""
        child_id = uuid.uuid4()

        assert str(child_id) not in statements.actor_key(child_id)


class TestWhatIsRefused:
    def test_a_statement_without_an_identifier(self) -> None:
        body = statement()
        del body["id"]

        with pytest.raises(ValidationException):
            statements.parse(body, KEY)

    def test_a_verb_the_platform_has_never_seen(self) -> None:
        with pytest.raises(ValidationException):
            statements.parse(statement(verb={"id": "http://example.org/verbs/x"}), KEY)

    def test_a_statement_naming_no_object(self) -> None:
        body = statement()
        del body["object"]

        with pytest.raises(ValidationException):
            statements.parse(body, KEY)

    def test_an_object_identifier_too_long_to_store(self) -> None:
        """Refused rather than shortened: truncation would merge two questions."""
        with pytest.raises(ValidationException):
            statements.parse(statement(object={"id": "http://x/" + "q" * 300}), KEY)

    def test_a_statement_larger_than_the_cap(self) -> None:
        with pytest.raises(ValidationException):
            statements.parse(
                statement(context={"padding": "x" * (MAX_STATEMENT_BYTES + 1)}), KEY
            )

    def test_a_success_that_is_not_a_boolean(self) -> None:
        with pytest.raises(ValidationException):
            statements.parse(statement(result={"success": "oui"}), KEY)

    def test_a_payload_that_is_not_an_object(self) -> None:
        with pytest.raises(ValidationException):
            statements.parse(["answered"], KEY)


class TestWhatIsKept:
    def test_an_unjudged_answer_stays_unjudged(self) -> None:
        """A content that says nothing about an answer is not made to say it."""
        parsed = statements.parse(statement(result={"response": "vrai"}), KEY)

        assert parsed.result_success is None

    def test_a_statement_without_a_result_says_nothing(self) -> None:
        body = statement()
        del body["result"]

        parsed = statements.parse(body, KEY)

        assert parsed.result_success is None and parsed.result_response is None

    def test_only_answered_becomes_a_response(self) -> None:
        assert statements.parse(statement(), KEY).is_answer
        assert not statements.parse(
            statement(verb={"id": VERB_COMPLETED}), KEY
        ).is_answer

    def test_the_source_timestamp_is_kept_as_a_claim(self) -> None:
        parsed = statements.parse(statement(), KEY)

        assert parsed.issued_at is not None
        assert parsed.issued_at.year == 2026

    def test_an_unreadable_timestamp_is_dropped_rather_than_refused(self) -> None:
        """It decides nothing here; losing the observation over it would cost more."""
        parsed = statements.parse(statement(timestamp="hier"), KEY)

        assert parsed.issued_at is None

    def test_the_rest_of_the_statement_survives_untouched(self) -> None:
        parsed = statements.parse(statement(context={"platform": "H5P"}), KEY)

        assert parsed.statement["context"] == {"platform": "H5P"}
