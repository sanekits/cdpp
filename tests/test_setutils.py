"""Tests for setutils.IndexedSet class."""
import pytest
from setutils import IndexedSet


class TestIndexedSetBasics:
    """Tests for basic IndexedSet operations."""
    
    def test_init_empty(self):
        """Test creating an empty IndexedSet."""
        s = IndexedSet()
        assert len(s) == 0
        assert list(s) == []
    
    def test_init_with_list(self):
        """Test creating IndexedSet from list."""
        s = IndexedSet([1, 2, 3])
        assert len(s) == 3
        assert list(s) == [1, 2, 3]
    
    def test_init_with_duplicates(self):
        """Test that duplicates are removed but order is preserved."""
        s = IndexedSet([1, 2, 3, 2, 4, 1])
        assert len(s) == 4
        assert list(s) == [1, 2, 3, 4]
    
    def test_add_new_item(self):
        """Test adding new item to set."""
        s = IndexedSet([1, 2])
        s.add(3)
        assert len(s) == 3
        assert 3 in s
        assert list(s) == [1, 2, 3]
    
    def test_add_existing_item(self):
        """Test adding existing item (should not duplicate)."""
        s = IndexedSet([1, 2, 3])
        s.add(2)
        assert len(s) == 3
        assert list(s) == [1, 2, 3]
    
    def test_contains(self):
        """Test membership checking."""
        s = IndexedSet([1, 2, 3])
        assert 1 in s
        assert 2 in s
        assert 3 in s
        assert 4 not in s
    
    def test_len(self):
        """Test length calculation."""
        s = IndexedSet([1, 2, 3])
        assert len(s) == 3
        s.add(4)
        assert len(s) == 4
    
    def test_iter(self):
        """Test iteration over set."""
        s = IndexedSet([1, 2, 3])
        items = list(s)
        assert items == [1, 2, 3]


class TestIndexedSetRemoval:
    """Tests for removal operations."""
    
    def test_remove_existing(self):
        """Test removing existing item."""
        s = IndexedSet([1, 2, 3])
        s.remove(2)
        assert len(s) == 2
        assert 2 not in s
        assert list(s) == [1, 3]
    
    def test_remove_nonexistent(self):
        """Test removing non-existent item raises KeyError."""
        s = IndexedSet([1, 2, 3])
        with pytest.raises(KeyError):
            s.remove(4)
    
    def test_discard_existing(self):
        """Test discarding existing item."""
        s = IndexedSet([1, 2, 3])
        s.discard(2)
        assert len(s) == 2
        assert 2 not in s
    
    def test_discard_nonexistent(self):
        """Test discarding non-existent item (should not raise)."""
        s = IndexedSet([1, 2, 3])
        s.discard(4)  # Should not raise
        assert len(s) == 3
    
    def test_clear(self):
        """Test clearing the set."""
        s = IndexedSet([1, 2, 3])
        s.clear()
        assert len(s) == 0
        assert list(s) == []
    
    def test_pop_default(self):
        """Test popping last item by default."""
        s = IndexedSet([1, 2, 3])
        item = s.pop()
        assert item == 3
        assert len(s) == 2
        assert list(s) == [1, 2]
    
    def test_pop_index(self):
        """Test popping item at specific index."""
        s = IndexedSet([1, 2, 3, 4])
        item = s.pop(1)
        assert item == 2
        assert len(s) == 3
        assert list(s) == [1, 3, 4]
    
    def test_pop_negative_index(self):
        """Test popping with negative index."""
        s = IndexedSet([1, 2, 3, 4])
        item = s.pop(-2)
        assert item == 3
        assert len(s) == 3
        assert list(s) == [1, 2, 4]


class TestIndexedSetSetOperations:
    """Tests for set operations."""
    
    def test_union(self):
        """Test union of sets."""
        s1 = IndexedSet([1, 2, 3])
        s2 = IndexedSet([3, 4, 5])
        result = s1.union(s2)
        assert len(result) == 5
        assert set(result) == {1, 2, 3, 4, 5}
    
    def test_union_operator(self):
        """Test union using | operator."""
        s1 = IndexedSet([1, 2, 3])
        s2 = IndexedSet([3, 4, 5])
        result = s1 | s2
        assert len(result) == 5
        assert set(result) == {1, 2, 3, 4, 5}
    
    def test_intersection(self):
        """Test intersection of sets."""
        s1 = IndexedSet([1, 2, 3, 4])
        s2 = IndexedSet([3, 4, 5, 6])
        result = s1.intersection(s2)
        assert len(result) == 2
        assert set(result) == {3, 4}
    
    def test_intersection_operator(self):
        """Test intersection using & operator."""
        s1 = IndexedSet([1, 2, 3, 4])
        s2 = IndexedSet([3, 4, 5, 6])
        result = s1 & s2
        assert len(result) == 2
        assert set(result) == {3, 4}
    
    def test_difference(self):
        """Test difference of sets."""
        s1 = IndexedSet([1, 2, 3, 4])
        s2 = IndexedSet([3, 4, 5, 6])
        result = s1.difference(s2)
        assert len(result) == 2
        assert set(result) == {1, 2}
    
    def test_difference_operator(self):
        """Test difference using - operator."""
        s1 = IndexedSet([1, 2, 3, 4])
        s2 = IndexedSet([3, 4, 5, 6])
        result = s1 - s2
        assert len(result) == 2
        assert set(result) == {1, 2}
    
    def test_symmetric_difference(self):
        """Test symmetric difference of sets."""
        s1 = IndexedSet([1, 2, 3, 4])
        s2 = IndexedSet([3, 4, 5, 6])
        result = s1.symmetric_difference(s2)
        assert len(result) == 4
        assert set(result) == {1, 2, 5, 6}
    
    def test_symmetric_difference_operator(self):
        """Test symmetric difference using ^ operator."""
        s1 = IndexedSet([1, 2, 3, 4])
        s2 = IndexedSet([3, 4, 5, 6])
        result = s1 ^ s2
        assert len(result) == 4
        assert set(result) == {1, 2, 5, 6}
    
    def test_issubset(self):
        """Test issubset check."""
        s1 = IndexedSet([1, 2])
        s2 = IndexedSet([1, 2, 3, 4])
        assert s1.issubset(s2) is True
        assert s2.issubset(s1) is False
    
    def test_issuperset(self):
        """Test issuperset check."""
        s1 = IndexedSet([1, 2, 3, 4])
        s2 = IndexedSet([1, 2])
        assert s1.issuperset(s2) is True
        assert s2.issuperset(s1) is False
    
    def test_isdisjoint(self):
        """Test isdisjoint check."""
        s1 = IndexedSet([1, 2, 3])
        s2 = IndexedSet([4, 5, 6])
        s3 = IndexedSet([3, 4, 5])
        assert s1.isdisjoint(s2) is True
        assert s1.isdisjoint(s3) is False


class TestIndexedSetInPlaceOperations:
    """Tests for in-place set operations."""
    
    def test_update(self):
        """Test update (in-place union)."""
        s = IndexedSet([1, 2, 3])
        s.update([3, 4, 5])
        assert len(s) == 5
        assert set(s) == {1, 2, 3, 4, 5}
    
    def test_intersection_update(self):
        """Test intersection_update."""
        s = IndexedSet([1, 2, 3, 4])
        s.intersection_update([3, 4, 5, 6])
        assert len(s) == 2
        assert set(s) == {3, 4}
    
    def test_difference_update(self):
        """Test difference_update."""
        s = IndexedSet([1, 2, 3, 4])
        s.difference_update([3, 4, 5, 6])
        assert len(s) == 2
        assert set(s) == {1, 2}
    
    def test_symmetric_difference_update(self):
        """Test symmetric_difference_update."""
        s = IndexedSet([1, 2, 3, 4])
        s.symmetric_difference_update([3, 4, 5, 6])
        assert len(s) == 4
        assert set(s) == {1, 2, 5, 6}


class TestIndexedSetIndexing:
    """Tests for list-like indexing operations."""
    
    def test_getitem_positive_index(self):
        """Test getting item by positive index."""
        s = IndexedSet([10, 20, 30, 40])
        assert s[0] == 10
        assert s[1] == 20
        assert s[2] == 30
        assert s[3] == 40
    
    def test_getitem_negative_index(self):
        """Test getting item by negative index."""
        s = IndexedSet([10, 20, 30, 40])
        assert s[-1] == 40
        assert s[-2] == 30
        assert s[-3] == 20
        assert s[-4] == 10
    
    def test_getitem_out_of_range(self):
        """Test that out of range index raises IndexError."""
        s = IndexedSet([1, 2, 3])
        with pytest.raises(IndexError):
            _ = s[10]
    
    def test_getitem_slice(self):
        """Test slicing."""
        s = IndexedSet([1, 2, 3, 4, 5])
        result = s[1:4]
        assert isinstance(result, IndexedSet)
        assert list(result) == [2, 3, 4]
    
    def test_getitem_slice_with_step(self):
        """Test slicing with step."""
        s = IndexedSet([1, 2, 3, 4, 5, 6])
        result = s[::2]
        assert list(result) == [1, 3, 5]
    
    def test_index(self):
        """Test finding index of value."""
        s = IndexedSet([10, 20, 30, 40])
        assert s.index(10) == 0
        assert s.index(20) == 1
        assert s.index(30) == 2
        assert s.index(40) == 3
    
    def test_index_not_found(self):
        """Test that index raises ValueError for missing value."""
        s = IndexedSet([1, 2, 3])
        with pytest.raises(ValueError):
            s.index(4)
    
    def test_count(self):
        """Test count method."""
        s = IndexedSet([1, 2, 3])
        assert s.count(1) == 1
        assert s.count(2) == 1
        assert s.count(4) == 0


class TestIndexedSetOrdering:
    """Tests for ordering operations."""
    
    def test_reverse(self):
        """Test reversing the set."""
        s = IndexedSet([1, 2, 3, 4])
        s.reverse()
        assert list(s) == [4, 3, 2, 1]
    
    def test_sort(self):
        """Test sorting the set."""
        s = IndexedSet([3, 1, 4, 2])
        s.sort()
        assert list(s) == [1, 2, 3, 4]
    
    def test_reversed(self):
        """Test __reversed__ iterator."""
        s = IndexedSet([1, 2, 3, 4])
        result = list(reversed(s))
        assert result == [4, 3, 2, 1]


class TestIndexedSetComparison:
    """Tests for comparison operations."""
    
    def test_equality_with_indexed_set(self):
        """Test equality between IndexedSets."""
        s1 = IndexedSet([1, 2, 3])
        s2 = IndexedSet([1, 2, 3])
        s3 = IndexedSet([3, 2, 1])  # Different order
        
        assert s1 == s2
        assert s1 != s3  # Order matters for IndexedSet
    
    def test_equality_with_set(self):
        """Test equality with regular set."""
        s1 = IndexedSet([1, 2, 3])
        s2 = {1, 2, 3}
        s3 = {1, 2, 3, 4}
        
        assert s1 == s2
        assert s1 != s3
    
    def test_repr(self):
        """Test string representation."""
        s = IndexedSet([1, 2, 3])
        assert repr(s) == "IndexedSet([1, 2, 3])"


class TestIndexedSetWithTuples:
    """Tests for IndexedSet with tuple entries (as used in navdex)."""
    
    def test_tuple_entries(self):
        """Test IndexedSet with tuple entries."""
        s = IndexedSet([("path1", 1), ("path2", 2)])
        assert len(s) == 2
        assert ("path1", 1) in s
        assert ("path2", 2) in s
    
    def test_tuple_union(self):
        """Test union with tuple entries."""
        s1 = IndexedSet([("a", 1), ("b", 2)])
        s2 = [("b", 2), ("c", 3)]
        result = s1.union(s2)
        assert len(result) == 3
        assert ("a", 1) in result
        assert ("b", 2) in result
        assert ("c", 3) in result
    
    def test_tuple_add_duplicate(self):
        """Test that duplicate tuples are not added."""
        s = IndexedSet([("path", 1)])
        s.add(("path", 1))
        assert len(s) == 1
    
    def test_tuple_sorting(self):
        """Test sorting tuples."""
        s = IndexedSet([("c", 3), ("a", 1), ("b", 2)])
        s.sort()
        result = list(s)
        assert result == [("a", 1), ("b", 2), ("c", 3)]
