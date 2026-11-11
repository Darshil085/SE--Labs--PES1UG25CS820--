
import pytest

from bookstore_trade_in import (
    process_book_buybacks,
    inspect_scanner_calibration,
)


def test_invalid_batches():
    with pytest.raises(ValueError):
        process_book_buybacks("invalid", 5.0)


def test_negative_bonus():
    with pytest.raises(ValueError):
        process_book_buybacks([], -1.0)


def test_unapproved_batch():
    result = process_book_buybacks(
        [{"intake_approved": False, "books": []}], 5.0
    )
    assert result["status"] == "ZERO_CREDIT"


def test_textbook_mint():
    batches = [{
        "intake_approved": True,
        "format": "textbook",
        "books": [{"condition": "mint"}],
    }]
    result = process_book_buybacks(batches, 5.0)
    assert result["total_payout"] == 50.0


def test_hardcover_poor():
    batches = [{
        "intake_approved": True,
        "format": "hardcover",
        "books": [{"condition": "poor"}],
    }]
    result = process_book_buybacks(batches, 5.0)
    assert result["total_payout"] == 6.0


def test_unknown_condition():
    batches = [{
        "intake_approved": True,
        "format": "paperback",
        "books": [{"condition": "average"}],
    }]
    result = process_book_buybacks(batches, 5.0)
    assert result["total_payout"] == 8.0


def test_unsupported_format():
    batches = [{
        "intake_approved": True,
        "format": "audio",
        "books": [{"condition": "good"}],
    }]
    result = process_book_buybacks(batches, 5.0)
    assert result["status"] == "ZERO_CREDIT"


def test_missing_pages():
    batches = [{
        "intake_approved": True,
        "format": "paperback",
        "books": [{"missing_pages": 2}],
    }]
    result = process_book_buybacks(batches, 5.0)
    assert result["status"] == "ZERO_CREDIT"


def test_counterfeit_paperback():
    batches = [{
        "intake_approved": True,
        "format": "paperback",
        "books": [{"counterfeit": True}],
    }]
    result = process_book_buybacks(batches, 5.0)
    assert result["status"] == "ZERO_CREDIT"


def test_counterfeit_textbook_breaks_batch():
    batches = [{
        "intake_approved": True,
        "format": "textbook",
        "books": [
            {"condition": "good"},
            {"counterfeit": True},
            {"condition": "mint"},
        ],
    }]
    result = process_book_buybacks(batches, 5.0)
    assert result["status"] == "ZERO_CREDIT"


def test_store_credit_bonus():
    batches = [{
        "intake_approved": True,
        "format": "paperback",
        "payout_in_credit": True,
        "books": [{"condition": "good"}],
    }]
    result = process_book_buybacks(batches, 5.0)
    assert result["total_payout"] == 13.0


def test_audit_rejected():
    batches = [{
        "intake_approved": True,
        "format": "paperback",
        "books": [{"missing_pages": 1} for _ in range(5)],
    }]
    result = process_book_buybacks(batches, 5.0)
    assert result["status"] == "AUDIT_REJECTED"


def test_empty_scanner_data():
    assert inspect_scanner_calibration([]) == "NO_DATA"


def test_scanner_calibrated():
    assert inspect_scanner_calibration([[1, 3, 5], [2, 4]]) == "CALIBRATED"


def test_scanner_recalibration():
    assert inspect_scanner_calibration([[6, 7]]) == "RECALIBRATE"