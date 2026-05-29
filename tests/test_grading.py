"""Tests for grading engine."""
import sys
sys.path.insert(0, "/Users/jos/dev/vox-python/src")

from grading.engine import calculate_grade, grade_to_council, GradeResult
from grading.technical import score_technical
from grading.fundamental import score_fundamental
from grading.delisted import check_ticker_status

def test_grade_to_council():
    """Test council signal mapping."""
    assert grade_to_council(95) == "STRONG_BUY"
    assert grade_to_council(80) == "BUY"
    assert grade_to_council(60) == "HOLD"
    assert grade_to_council(30) == "SELL"
    assert grade_to_council(10) == "STRONG_SELL"
    print("✅ test_grade_to_council passed")

def test_score_technical_aapl():
    """Test technical scoring for AAPL."""
    result = score_technical("AAPL")
    assert "score" in result
    assert 0 <= result["score"] <= 100
    assert "rsi" in result
    assert "macd_bullish" in result
    print(f"✅ test_score_technical_aapl passed (score: {result['score']})")

def test_score_fundamental_aapl():
    """Test fundamental scoring for AAPL."""
    result = score_fundamental("AAPL")
    assert "score" in result
    assert 0 <= result["score"] <= 100
    print(f"✅ test_score_fundamental_aapl passed (score: {result['score']})")

def test_calculate_grade_aapl():
    """Test full grade calculation for AAPL."""
    result = calculate_grade("AAPL")
    assert isinstance(result, GradeResult)
    assert 0 <= result.overall_grade <= 100
    assert result.council in ["STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL"]
    print(f"✅ test_calculate_grade_aapl passed (grade: {result.overall_grade}, council: {result.council})")

def test_delisted_lilm():
    """Test that LILM is detected as delisted."""
    result = check_ticker_status("LILM")
    assert result["delisted"] == True
    assert result["valid"] == False
    print("✅ test_delisted_lilm passed")

def test_valid_tsla():
    """Test that TSLA is detected as valid."""
    result = check_ticker_status("TSLA")
    assert result["valid"] == True
    assert result["delisted"] == False
    print("✅ test_valid_tsla passed")

def run_all_tests():
    """Run all tests."""
    print("Running VOX grading tests...\n")
    
    tests = [
        test_grade_to_council,
        test_score_technical_aapl,
        test_score_fundamental_aapl,
        test_calculate_grade_aapl,
        test_delisted_lilm,
        test_valid_tsla,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} FAILED: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*50}")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
