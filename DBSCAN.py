import numpy as np
from collections import deque
from typing import Optional


class DBSCAN:
    """
    Density-based spatial clustering of applications with noise (DBSCAN).

    Parameters
    ----------
    eps : float
        Neighborhood radius. Points within this distance are considered neighbors.
    min_pts : int
        Minimum number of points required to form a dense (core) region.
    metric : str
        Distance metric to use. One of {'euclidean', 'manhattan', 'chebyshev'}.

    Attributes
    ----------
    labels_ : np.ndarray of shape (n_samples,)
        Cluster labels for each point after calling fit().
        Labels of -1 indicate noise points.
    core_sample_indices_ : np.ndarray
        Indices of core points found during fit().
    n_clusters_ : int
        Number of clusters found (excluding noise).
    n_noise_ : int
        Number of points labeled as noise.

    Examples
    --------
    >>> import numpy as np
    >>> X = np.array([[1, 2], [1.1, 2], [5, 6], [5.1, 6]])
    >>> db = DBSCAN(eps=0.5, min_pts=2).fit(X)
    >>> db.labels_
    array([0, 0, 1, 1])
    """

    # Supported distance metrics
    _METRICS = ('euclidean', 'manhattan', 'chebyshev')

    def __init__(self, eps: float = 0.5, min_pts: int = 5, metric: str = 'euclidean'):
        if eps <= 0:
            raise ValueError(f"eps must be positive, got {eps}")
        if min_pts < 1:
            raise ValueError(f"min_pts must be >= 1, got {min_pts}")
        if metric not in self._METRICS:
            raise ValueError(f"metric must be one of {self._METRICS}, got '{metric}'")

        self.eps = eps
        self.min_pts = min_pts
        self.metric = metric

        # Set after fit()
        self.labels_: Optional[np.ndarray] = None
        self.core_sample_indices_: Optional[np.ndarray] = None
        self.n_clusters_: int = 0
        self.n_noise_: int = 0

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _compute_distance_matrix(self, X: np.ndarray) -> np.ndarray:
        """
        Compute the pairwise distance matrix for all points in X.

        Uses vectorized operations throughout to avoid Python-level loops.
        Memory cost is O(n²) — acceptable for small/medium datasets.
        For large datasets (n > ~10 000) consider a KD-tree approach instead.
        """
        if self.metric == 'euclidean':
            # Numerically stable squared-distance trick: avoids X[:, None] - X[None, :]
            # which allocates an (n, n, d) intermediate tensor.
            # ||a - b||² = ||a||² + ||b||² - 2 a·b
            sq = np.einsum('ij,ij->i', X, X)               # (n,)
            dists = np.sqrt(
                np.maximum(sq[:, None] + sq[None, :] - 2 * X @ X.T, 0.0)
            )
        elif self.metric == 'manhattan':
            dists = np.abs(X[:, None] - X[None, :]).sum(axis=2)
        else:  # chebyshev
            dists = np.abs(X[:, None] - X[None, :]).max(axis=2)

        return dists

    def _region_query(self, dists: np.ndarray, idx: int) -> np.ndarray:
        """Return indices of all points within eps of point idx (including itself)."""
        return np.where(dists[idx] <= self.eps)[0]

    def _expand_cluster(
        self,
        dists: np.ndarray,
        visited: np.ndarray,
        cluster_id: int,
        seed_neighbors: np.ndarray,
    ) -> None:
        """
        Grow a cluster by BFS from its initial seed neighbors.

        Modifies self.labels_ and visited in-place.
        """
        queue = deque(seed_neighbors)

        while queue:
            j = queue.popleft()

            # Label unassigned points (noise OR unvisited) as part of this cluster
            if self.labels_[j] == -1:
                self.labels_[j] = cluster_id

            if visited[j]:
                continue

            visited[j] = True
            j_neighbors = self._region_query(dists, j)

            # Only core points expand the frontier
            if j_neighbors.size >= self.min_pts:
                queue.extend(j_neighbors)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def fit(self, X: np.ndarray) -> "DBSCAN":
        """
        Perform DBSCAN clustering on X.

        Parameters
        ----------
        X : np.ndarray of shape (n_samples, n_features)

        Returns
        -------
        self : fitted DBSCAN instance
        """
        X = np.asarray(X, dtype=float)

        if X.ndim != 2:
            raise ValueError(f"X must be 2-D, got shape {X.shape}")
        if X.shape[0] < 1:
            raise ValueError("X must contain at least one sample.")

        n = X.shape[0]
        self.labels_ = np.full(n, -1, dtype=int)    # everyone starts as noise
        visited = np.zeros(n, dtype=bool)

        dists = self._compute_distance_matrix(X)

        cluster_id = 0
        core_indices = []

        for i in range(n):
            if visited[i]:
                continue

            visited[i] = True
            neighbors = self._region_query(dists, i)

            # --- Not a core point: leave as noise for now ---
            if neighbors.size < self.min_pts:
                continue

            # --- Core point: start a new cluster ---
            core_indices.append(i)
            self.labels_[i] = cluster_id
            self._expand_cluster(dists, visited, cluster_id, neighbors)

            cluster_id += 1

        # Store summary statistics
        self.core_sample_indices_ = np.array(core_indices, dtype=int)
        self.n_clusters_ = cluster_id
        self.n_noise_ = int(np.sum(self.labels_ == -1))

        return self

    def fit_predict(self, X: np.ndarray) -> np.ndarray:
        """Fit and return labels in one step."""
        return self.fit(X).labels_

    def __repr__(self) -> str:
        return (
            f"DBSCAN(eps={self.eps}, min_pts={self.min_pts}, metric='{self.metric}')\n"
            f"  Clusters : {self.n_clusters_}\n"
            f"  Noise pts: {self.n_noise_}"
        )
