# tests/domain/entities/test_t2_stats.py
import pytest
import sys
from pathlib import Path

# Ajouter src/ au path pour pouvoir importer
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from domain.entities.t2_stats import T2Stats


def test_create_valid_t2stats():
    """Test : Create a T2stat with valid values"""
    mean = 35.2
    sd = 2.1
    
    stats = T2Stats(mean=mean, sd=sd)
    
    assert stats.mean == 35.2
    assert stats.sd == 2.1


def test_t2stats_repr():
    """Test : Check the representaion string"""
    stats = T2Stats(mean=35.2, sd=2.1)
    result = repr(stats)
    assert result == "T2(mean=35.2, sd=2.1)"


def test_negative_mean_raises_error():
    """Test : mean < 0 should raise ValueError"""
    with pytest.raises(ValueError):
        T2Stats(mean=-50, sd=2.1)


def test_negative_sd_raises_error():
    """Test : sd <0 should raise ValueError"""
    with pytest.raises(ValueError):
        T2Stats(mean=35, sd=-8)


def test_equality():
    """Test : Identical T2Stats are equal"""
    stats1 = T2Stats(mean=31.0, sd=2.0)
    stats2 = T2Stats(mean=31.0, sd=2.0)
    assert stats1 == stats2


def test_inequality():
    """Test : Different T2Stats are not equal"""
    stats1 = T2Stats(mean=31.0, sd=2.0)
    stats2 = T2Stats(mean=31.5, sd=2.0)
    assert stats1 != stats2