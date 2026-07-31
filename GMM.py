import numpy as np
from numpy.linalg import slogdet, inv


class GMM:
    """
    Gaussian Mixture Model via Expectation‑Maximization.

        • n_components : number of Gaussian clusters (K)
        • tol          : convergence threshold on log‑likelihood
        • max_iter     : maximum EM iterations
    """

    def __init__(self, n_components=2, tol=1e-4, max_iter=200, seed=None):
        self.K = n_components
        self.tol = tol
        self.max_iter = max_iter
        self.rng = np.random.default_rng(seed)

        # Learned parameters
        self.pi_ = None          # mixing weights, shape (K,)
        self.mu_ = None          # means,          shape (K, d)
        self.Sigma_ = None       # covariances,    shape (K, d, d)

    # ────────────────────────── helpers ──────────────────────────
    def _init_params(self, X):
        n, d = X.shape
        # Choose K random points as initial means
        self.mu_ = X[self.rng.choice(n, self.K, replace=False)]
        self.Sigma_ = np.array([np.cov(X, rowvar=False) + 1e-6 * np.eye(d)
                                for _ in range(self.K)])
        self.pi_ = np.full(self.K, 1 / self.K)

    def _gauss_pdf(self, X, k):
        """
        Multivariate normal density for component k at all points X.
        Returns shape (n,)
        """
        d = X.shape[1]
        diff = X - self.mu_[k]
        inv_cov = inv(self.Sigma_[k])
        _, logdet = slogdet(self.Sigma_[k])

        exponent = np.einsum("ij,jk,ik->i", diff, inv_cov, diff)
        return np.exp(-0.5 * exponent) / np.sqrt((2 * np.pi) ** d * np.exp(logdet))

    # ─────────────────────────── API ────────────────────────────
    def fit(self, X):
        X = np.asarray(X, dtype=float)
        n, d = X.shape
        self._init_params(X)

        prev_ll = -np.inf
        for it in range(self.max_iter):
            # E‑step: responsibilities γ_{ik}
            pdfs = np.stack([self._gauss_pdf(X, k) for k in range(self.K)], axis=1)
            numerator = self.pi_ * pdfs                  # shape (n, K)
            gamma = numerator / numerator.sum(axis=1, keepdims=True)

            # M‑step: update parameters
            Nk = gamma.sum(axis=0)                       # shape (K,)
            self.pi_ = Nk / n
            self.mu_ = (gamma.T @ X) / Nk[:, None]

            for k in range(self.K):
                diff = X - self.mu_[k]
                self.Sigma_[k] = (gamma[:, k][:, None] * diff).T @ diff / Nk[k]
                # Regularize for numerical stability
                self.Sigma_[k] += 1e-6 * np.eye(d)

            # Log‑likelihood
            ll = np.sum(np.log((self.pi_ * pdfs).sum(axis=1)))
            if np.abs(ll - prev_ll) < self.tol:
                break
            prev_ll = ll
        return self

    def predict(self, X):
        """
        Hard cluster assignment (argmax responsibility).
        """
        pdfs = np.stack([self._gauss_pdf(X, k) for k in range(self.K)], axis=1)
        return np.argmax(self.pi_ * pdfs, axis=1)

    def score_samples(self, X):
        """
        Log‑probability of each sample under the fitted mixture.
        """
        pdfs = np.stack([self._gauss_pdf(X, k) for k in range(self.K)], axis=1)
        return np.log((self.pi_ * pdfs).sum(axis=1))


# ─────────────────────────── demo ────────────────────────────
if __name__ == "__main__":
    # Synthetic 2‑D data from three Gaussians
    n = 900
    centers = np.array([[0, 0], [5, 5], [-4, 4]])
    covs = [np.array([[1.0, 0.3], [0.3, 1.2]]),
            np.array([[0.5, -0.2], [-0.2, 0.7]]),
            np.array([[0.8, 0], [0, 0.4]])]

    rng = np.random.default_rng(0)
    X = np.vstack([
        rng.multivariate_normal(centers[i], covs[i], n // 3)
        for i in range(3)
    ])

    gmm = GMM(n_components=3, seed=0)
    gmm.fit(X)
    labels = gmm.predict(X)

    print("First 15 labels:", labels[:15])
    # Optional: plot with matplotlib to see clusters
