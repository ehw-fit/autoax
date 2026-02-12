import numpy as np


class ParetoFront:
    """Maintains a Pareto front for multi-objective optimization.

    Compatible with PyBspTreeArchive interface used in the search scripts.
    """

    def __init__(self, num_objectives, minimize=None):
        """
        Args:
            num_objectives: Number of objectives.
            minimize: List of bools indicating whether each objective should be
                minimized (True) or maximized (False). If None, all objectives
                are minimized.
        """
        self.num_objectives = num_objectives
        if minimize is None:
            self.minimize = [True] * num_objectives
        else:
            assert len(minimize) == num_objectives
            self.minimize = list(minimize)
        # sign multiplier: +1 for minimize, -1 for maximize (we internally
        # store values so that lower is always better)
        self._sign = np.array([1.0 if m else -1.0 for m in self.minimize])
        self._points = {}  # id -> normalized objective values (np.array)
        self._next_id = 0

    def _normalize(self, objectives):
        return np.asarray(objectives, dtype=float) * self._sign

    def _dominates(self, a, b):
        """Return True if point a dominates point b (all <= and at least one <)."""
        return bool(np.all(a <= b) and np.any(a < b))

    def process(self, objectives, returnId=True):
        """Insert a point if it is not dominated by any existing point.

        Args:
            objectives: List/array of objective values.
            returnId: If True, return (is_pareto, id). If False, return is_pareto.

        Returns:
            If returnId is True: (dominated: bool, point_id: int)
                dominated is True if the point was added to the front.
            If returnId is False: dominated (bool)
        """
        norm = self._normalize(objectives)

        # Check if the new point is dominated by any existing point
        for pid, existing in self._points.items():
            if self._dominates(existing, norm):
                # New point is dominated — reject it
                if returnId:
                    return False, -1
                return False

        # The new point is non-dominated — remove points it dominates
        to_remove = [
            pid for pid, existing in self._points.items()
            if self._dominates(norm, existing)
        ]
        for pid in to_remove:
            del self._points[pid]

        # Add the new point
        cid = self._next_id
        self._next_id += 1
        self._points[cid] = norm

        if returnId:
            return True, cid
        return True

    def filter(self, objectives_list, returnIds=False):
        """Filter a list of points, returning only the non-dominated ones.

        Args:
            objectives_list: List of objective vectors.
            returnIds: If True, return indices into the original list.
                If False, return the objective vectors themselves.

        Returns:
            List of indices (returnIds=True) or objective vectors (returnIds=False).
        """
        norms = [self._normalize(obj) for obj in objectives_list]
        non_dominated = []

        for i, ni in enumerate(norms):
            dominated = False
            for j, nj in enumerate(norms):
                if i != j and self._dominates(nj, ni):
                    dominated = True
                    break
            if not dominated:
                non_dominated.append(i)

        if returnIds:
            return non_dominated
        return [objectives_list[i] for i in non_dominated]

    def points(self, returnIds=False):
        """Return the current Pareto-optimal points.

        Args:
            returnIds: If True, return list of point IDs. If False, return
                list of original (un-normalized) objective values.
        """
        if returnIds:
            return list(self._points.keys())
        return [vals * self._sign for vals in self._points.values()]

    def size(self):
        """Return the number of points on the Pareto front."""
        return len(self._points)


def pareto(df, objectives, minimize=None):
    """Filter a pandas DataFrame to keep only Pareto-optimal rows.

    Args:
        df: pandas DataFrame.
        objectives: List of column names to use as objectives.
        minimize: List of bools (True=minimize, False=maximize) per objective.
            If None, all objectives are minimized.

    Returns:
        Filtered DataFrame containing only non-dominated rows.
    """
    pf = ParetoFront(len(objectives), minimize=minimize)
    values = df[objectives].values.tolist()
    ids = pf.filter(values, returnIds=True)
    return df.iloc[ids]
