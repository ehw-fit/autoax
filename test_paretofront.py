import numpy as np
import pytest
from paretofront import ParetoFront


# ── 2D tests ──────────────────────────────────────────────────────────────────

class TestParetoFront2D:
    """2-objective Pareto front (minimize obj1, maximize obj2)."""

    def _make_pf(self):
        return ParetoFront(2, minimize=[True, False])

    def test_first_point_always_accepted(self):
        pf = self._make_pf()
        ok, cid = pf.process([5, 10])
        assert ok is True
        assert pf.size() == 1

    def test_dominated_point_rejected(self):
        pf = self._make_pf()
        pf.process([3, 10])          # low cost, high quality
        ok, cid = pf.process([5, 8]) # worse in both objectives
        assert ok is False
        assert cid == -1
        assert pf.size() == 1

    def test_dominating_point_replaces(self):
        pf = self._make_pf()
        pf.process([5, 8])
        ok, cid = pf.process([3, 10])  # better in both
        assert ok is True
        assert pf.size() == 1

    def test_non_dominated_points_coexist(self):
        pf = self._make_pf()
        pf.process([1, 5])   # low cost, low quality
        pf.process([5, 10])  # high cost, high quality
        assert pf.size() == 2

    def test_new_point_prunes_multiple(self):
        pf = self._make_pf()  # min obj1, max obj2
        pf.process([2, 8])   # low cost, high quality
        pf.process([4, 10])  # mid cost, highest quality
        pf.process([6, 12])  # high cost, even higher quality
        assert pf.size() == 3
        # This point dominates all three (lower cost, higher quality)
        ok, _ = pf.process([1, 13])
        assert ok is True
        assert pf.size() == 1

    def test_equal_point_not_dominating(self):
        """An identical point should be added (not dominated, not dominating)."""
        pf = self._make_pf()
        pf.process([3, 5])
        ok, _ = pf.process([3, 5])
        # Equal is not strictly dominated, so it's accepted
        assert ok is True
        assert pf.size() == 2

    def test_points_returns_ids(self):
        pf = self._make_pf()
        _, id1 = pf.process([1, 5])
        _, id2 = pf.process([5, 10])
        ids = pf.points(returnIds=True)
        assert set(ids) == {id1, id2}

    def test_points_returns_values(self):
        pf = self._make_pf()
        pf.process([1, 5])
        pf.process([5, 10])
        vals = pf.points(returnIds=False)
        expected = {(1.0, 5.0), (5.0, 10.0)}
        actual = {tuple(v) for v in vals}
        assert actual == expected

    def test_process_without_returnId(self):
        pf = self._make_pf()  # min obj1, max obj2
        result = pf.process([3, 5], returnId=False)
        assert result is True
        result = pf.process([10, 15], returnId=False)  # worse obj1, better obj2
        assert result is True
        result = pf.process([10, 10], returnId=False)   # dominated by [10, 15]
        assert result is False

    def test_both_minimize(self):
        pf = ParetoFront(2, minimize=[True, True])
        pf.process([1, 5])
        pf.process([5, 1])
        assert pf.size() == 2
        # [1,1] dominates both
        pf.process([1, 1])
        assert pf.size() == 1

    def test_both_maximize(self):
        pf = ParetoFront(2, minimize=[False, False])
        pf.process([1, 5])
        pf.process([5, 1])
        assert pf.size() == 2
        # [5,5] dominates both
        pf.process([5, 5])
        assert pf.size() == 1

    def test_classic_pareto_front(self):
        """Insert points along f2 = 1/f1 curve — all should be non-dominated."""
        pf = ParetoFront(2, minimize=[True, True])
        for x in [1, 2, 4, 5, 10]:
            pf.process([x, 100.0 / x])
        assert pf.size() == 5

    def test_large_batch(self):
        """Stress test: insert many random points, verify no point on the front
        is dominated by another."""
        rng = np.random.RandomState(42)
        pf = ParetoFront(2, minimize=[True, False])
        stored = {}
        for _ in range(500):
            pt = rng.rand(2).tolist()
            ok, cid = pf.process(pt)
            if ok:
                stored[cid] = pt

        # Keep only surviving points
        surviving_ids = set(pf.points(returnIds=True))
        front = [stored[i] for i in surviving_ids if i in stored]

        # No point on the front should dominate another
        for i, a in enumerate(front):
            for j, b in enumerate(front):
                if i == j:
                    continue
                # a should NOT dominate b (min obj1, max obj2)
                a_dom_b = a[0] <= b[0] and a[1] >= b[1] and (a[0] < b[0] or a[1] > b[1])
                assert not a_dom_b, f"Point {a} dominates {b} on the front"


# ── 3D tests ──────────────────────────────────────────────────────────────────

class TestParetoFront3D:
    """3-objective Pareto front."""

    def _make_pf(self, minimize=None):
        if minimize is None:
            minimize = [True, True, False]
        return ParetoFront(3, minimize=minimize)

    def test_first_point(self):
        pf = self._make_pf()
        ok, _ = pf.process([1, 2, 3])
        assert ok is True
        assert pf.size() == 1

    def test_dominated_in_all_three(self):
        pf = self._make_pf()  # min, min, max
        pf.process([1, 1, 10])
        ok, _ = pf.process([2, 2, 5])  # worse in all three
        assert ok is False
        assert pf.size() == 1

    def test_dominating_in_all_three(self):
        pf = self._make_pf()  # min, min, max
        pf.process([5, 5, 1])
        ok, _ = pf.process([1, 1, 10])  # better in all three
        assert ok is True
        assert pf.size() == 1

    def test_non_dominated_3d(self):
        pf = self._make_pf()  # min, min, max
        pf.process([1, 5, 5])   # good obj1, bad obj2
        pf.process([5, 1, 5])   # bad obj1, good obj2
        pf.process([3, 3, 10])  # mid obj1/2, great obj3
        assert pf.size() == 3

    def test_partial_domination_not_sufficient(self):
        """Better in 2 of 3, equal in the third — still dominates."""
        pf = self._make_pf()  # min, min, max
        pf.process([3, 3, 5])
        ok, _ = pf.process([3, 3, 6])  # equal obj1/2, better obj3
        assert ok is True
        assert pf.size() == 1  # old point was dominated

    def test_worse_in_one_not_dominated(self):
        """Better in 2 objectives but worse in 1 — not dominated, coexists."""
        pf = self._make_pf()  # min, min, max
        pf.process([1, 5, 10])
        ok, _ = pf.process([2, 1, 10])  # worse obj1, better obj2, equal obj3
        assert ok is True
        assert pf.size() == 2

    def test_cascade_pruning(self):
        """A single point can prune multiple existing points in 3D."""
        pf = self._make_pf()  # min, min, max
        pf.process([3, 5, 10])  # good obj1, bad obj2
        pf.process([5, 3, 10])  # bad obj1, good obj2
        pf.process([4, 4, 12])  # mid obj1/2, great obj3
        assert pf.size() == 3
        ok, _ = pf.process([2, 2, 13])  # dominates all three
        assert ok is True
        assert pf.size() == 1

    def test_all_minimize_3d(self):
        pf = ParetoFront(3, minimize=[True, True, True])
        pf.process([1, 5, 5])
        pf.process([5, 1, 5])
        pf.process([5, 5, 1])
        assert pf.size() == 3
        # [1,1,1] dominates all
        pf.process([1, 1, 1])
        assert pf.size() == 1

    def test_all_maximize_3d(self):
        pf = ParetoFront(3, minimize=[False, False, False])
        pf.process([1, 5, 5])
        pf.process([5, 1, 5])
        pf.process([5, 5, 1])
        assert pf.size() == 3
        # [5,5,5] dominates all
        pf.process([5, 5, 5])
        assert pf.size() == 1

    def test_points_values_3d(self):
        pf = self._make_pf()  # min, min, max
        pf.process([1, 2, 3])
        pf.process([3, 1, 5])
        vals = pf.points(returnIds=False)
        expected = {(1.0, 2.0, 3.0), (3.0, 1.0, 5.0)}
        actual = {tuple(v) for v in vals}
        assert actual == expected

    def test_large_batch_3d(self):
        """Stress test for 3D: verify Pareto front integrity."""
        rng = np.random.RandomState(123)
        minimize = [True, False, True]
        sign = np.array([1.0, -1.0, 1.0])
        pf = ParetoFront(3, minimize=minimize)
        stored = {}

        for _ in range(500):
            pt = rng.rand(3).tolist()
            ok, cid = pf.process(pt)
            if ok:
                stored[cid] = np.array(pt)

        surviving_ids = set(pf.points(returnIds=True))
        front = [stored[i] for i in surviving_ids if i in stored]

        # Verify no point on the front dominates another
        for i, a in enumerate(front):
            for j, b in enumerate(front):
                if i == j:
                    continue
                an = a * sign
                bn = b * sign
                dominates = bool(np.all(an <= bn) and np.any(an < bn))
                assert not dominates, f"Point {a} dominates {b} on the 3D front"


# ── Edge cases ────────────────────────────────────────────────────────────────

class TestParetoFrontEdge:

    def test_empty_front(self):
        pf = ParetoFront(2)
        assert pf.size() == 0
        assert pf.points(returnIds=True) == []
        assert pf.points(returnIds=False) == []

    def test_default_minimize(self):
        pf = ParetoFront(3)
        assert pf.minimize == [True, True, True]

    def test_ids_are_unique_and_monotonic(self):
        pf = ParetoFront(2, minimize=[True, True])
        ids = []
        for x in range(10):
            ok, cid = pf.process([x, 10 - x])
            assert ok is True
            ids.append(cid)
        assert ids == sorted(ids)
        assert len(set(ids)) == len(ids)
