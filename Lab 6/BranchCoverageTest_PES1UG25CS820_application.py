
import pytest

from bookstore_trade_in import (
    process_book_buybacks,
    inspect_scanner_calibration,
)


def test_invalid_batches_type():
    with pytest.raises(ValueError):
        process_book_buybacks("invalid", 5.0)


def test_negative_bonus():
    with pytest.raises(ValueError):
        process_book_buybacks([], -1.0)


def test_all_book_formats_and_conditions():
    batches = [
        {
            "intake_approved": True,
            "format": "textbook",
            "books": [
                {"condition": "mint"},
                {"condition": "poor"},
                {"condition": "good"},
            ],
        },
        {
            "intake_approved": True,
            "format": "hardcover",
            "books": [{"condition": "poor"}],
        },
        {
            "intake_approved": True,
            "format": "paperback",
            "books": [{"condition": "good"}],
        },
    ]
    result = process_book_buybacks(batches, 5.0)
    assert result["total_payout"] == 120.0
    assert result["status"] == "COMPLETED"


def test_unapproved_batch_and_default_values():
    result = process_book_buybacks(
        [
            {"intake_approved": False},
            {"intake_approved": True, "books": [{}]},
        ],
        0.0,
    )
    assert result["total_payout"] == 8.0
    assert result["status"] == "COMPLETED"


def test_unsupported_format():
    result = process_book_buybacks(
        [{"intake_approved": True, "format": "audio"}], 0.0
    )
    assert result["status"] == "ZERO_CREDIT"


def test_missing_pages_rejection():
    result = process_book_buybacks(
        [{
            "intake_approved": True,
            "books": [{"missing_pages": 1}],
        }],
        0.0,
    )
    assert result["status"] == "ZERO_CREDIT"


def test_counterfeit_paperback_and_hardcover():
    result = process_book_buybacks(
        [
            {
                "intake_approved": True,
                "format": "paperback",
                "books": [{"counterfeit": True}],
            },
            {
                "intake_approved": True,
                "format": "hardcover",
                "books": [{"counterfeit": True}],
            },
        ],
        0.0,
    )
    assert result["status"] == "ZERO_CREDIT"


def test_counterfeit_textbook_breaks_loop():
    result = process_book_buybacks(
        [{
            "intake_approved": True,
            "format": "textbook",
            "books": [
                {"condition": "good"},
                {"counterfeit": True},
                {"condition": "mint"},
            ],
        }],
        0.0,
    )
    assert result["status"] == "ZERO_CREDIT"


def test_store_credit_bonus():
    result = process_book_buybacks(
        [{
            "intake_approved": True,
            "payout_in_credit": True,
            "books": [{"condition": "good"}],
        }],
        5.0,
    )
    assert result["total_payout"] == 13.0


def test_audit_rejection():
    result = process_book_buybacks(
        [{
            "intake_approved": True,
            "books": [{"missing_pages": 1} for _ in range(5)],
        }],
        0.0,
    )
    assert result["status"] == "AUDIT_REJECTED"


def test_scanner_no_data():
    assert inspect_scanner_calibration([]) == "NO_DATA"


def test_scanner_calibrated_and_reset_streak():
    assert inspect_scanner_calibration([[6, 1, 6]]) == "CALIBRATED"


def test_scanner_recalibration_same_device():
    assert inspect_scanner_calibration([[6, 7]]) == "RECALIBRATE"


def test_scanner_recalibration_multiple_devices():
    assert inspect_scanner_calibration([[1, 2], [6, 8]]) == "RECALIBRATE"