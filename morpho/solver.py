"""Implement the solver."""

from typing import List

import matplotlib.pyplot as plt
import numpy as np
from scipy.linalg import eigh

from .brillouinzone import BrillouinZonePath as BZPath
from .geometry import Geometry
from .utils import convmat


class Solver:
    """Implement the PWE solver."""

    def __init__(self,
                 geometry: Geometry,
                 path: BZPath,
                 P: int = 1,
                 Q: int = 1,
                 R: int = 1):
        """Initialize the PWE Solver."""
        self.geo = geometry
        self.path = path
        self.P, self.Q, self.R = P, Q, R
        self.eps_rc: np.ndarray
        self.mu_rc: np.ndarray

        self.wn: List[np.ndarray] = []
        self.modes: List[np.ndarray] = []

    def run(self):
        """Run the simulation."""
        self.geo.setup()
        self.eps_rc = convmat(self.geo.eps_r, self.P, self.Q, self.R)
        self.mu_rc = convmat(self.geo.mu_r, self.P, self.Q, self.R)

        eps_rk = np.kron(np.eye(3), self.eps_rc)
        # mu_rk = np.kron(np.eye(3), self.eps_rc)
        # epsr_ki = np.kron(np.eye(3), np.linalg.inv(self.eps_rc))
        mu_rki = np.kron(np.eye(3), np.linalg.inv(self.mu_rc))

        p = np.arange(-(self.P // 2), self.P // 2 + 1)
        q = np.arange(-(self.Q // 2), self.Q // 2 + 1)
        r = np.arange(-(self.R // 2), self.R // 2 + 1)

        P0, Q0, R0 = np.meshgrid(p, q, r)
        T1, T2, T3 = self.geo._T1, self.geo._T2, self.geo._T3

        G_k = (T1[:, None] * P0.flatten() + T2[:, None] * Q0.flatten() +
               T3[:, None] * R0.flatten())
        beta = self.path.beta_vec
        for col in range(beta.shape[1]):
            k = beta[:, col, None] - G_k

            KX = np.diag(k[0, :])
            KY = np.diag(k[1, :])
            KZ = np.diag(k[2, :])
            K_V = np.vstack((
                np.hstack((0 * KX, -KZ, KY)),
                np.hstack((KZ, 0 * KY, -KX)),
                np.hstack((-KY, KX, 0 * KZ)),
            ))
            A = K_V @ mu_rki @ K_V
            B = eps_rk

            D, V = eigh(A, B)

            self.wn.append(np.sqrt(-np.minimum(D, 0)))
            self.modes.append(V)

    def plot_bands(self):
        """Plot a bandgap diagram."""
        beta_len = self.path.beta_vec_len
        wn = np.vstack([d for d in self.wn])
        fig, ax = plt.subplots()
        ax.plot(beta_len, wn / (2 * np.pi), "k-")
        ax.set_xticklabels(self.path.symmetry_names)
        ax.set_xticks(self.path.symmetry_locations)
        ax.set_xlim(0, self.path.symmetry_locations[-1])
        ax.set_ylim(0, 2)
        ax.set_xlabel(r"Bloch Wave Vector $\beta$")
        ax.set_ylabel(r"Frequency $\frac{\omega a}{2\pi c}$")
        ax.grid(True)
        plt.show()


class Solver2D:
    """Implement the PWE solver."""

    def __init__(self,
                 geometry: Geometry,
                 path: BZPath,
                 P: int = 1,
                 Q: int = 1,
                 pol: str = "TM"):
        """Initialize the PWE Solver."""
        self.geo = geometry
        self.path = path
        self.P, self.Q = P, Q
        self.eps_rc: np.ndarray
        self.mu_rc: np.ndarray
        self.pol = pol

        self.wn: List[np.ndarray] = []
        self.modes: List[np.ndarray] = []

    def run(self):
        """Run the simulation."""
        self.geo.setup()
        self.eps_rc = convmat(self.geo.eps_r, self.P, self.Q, 1)
        self.mu_rc = convmat(self.geo.mu_r, self.P, self.Q, 1)

        mu_rci = np.linalg.inv(self.mu_rc)
        eps_rci = np.linalg.inv(self.eps_rc)

        p = np.arange(-(self.P // 2), self.P // 2 + 1)
        q = np.arange(-(self.Q // 2), self.Q // 2 + 1)

        P0, Q0 = np.meshgrid(p, q)
        T1, T2 = self.path.T1, self.path.T2

        G_k = P0.flatten() * T1[:, None] + Q0.flatten() * T2[:, None]
        beta = self.path.beta_vec
        for col in range(beta.shape[1]):
            k = beta[:, col, None] - G_k

            KX = np.diag(k[0, :])
            KY = np.diag(k[1, :])

            if self.pol == "TM":
                A = KX@mu_rci@KX + KY@mu_rci@KY
                B = self.eps_rc
            else:
                A = KX@eps_rci@KX + KY@eps_rci@KY
                B = self.mu_rc

            D, V = eigh(A, B)

            self.wn.append(np.sqrt(np.maximum(D, 0)))
            self.modes.append(V)

    def plot_bands(self):
        """Plot a bandgap diagram."""
        beta_len = self.path.beta_vec_len
        wn = np.vstack([d for d in self.wn])
        fig, ax = plt.subplots()
        ax.plot(beta_len, wn / (2 * np.pi), "k-")
        ax.set_xticklabels(self.path.symmetry_names)
        ax.set_xticks(self.path.symmetry_locations)
        ax.set_xlim(0, self.path.symmetry_locations[-1])
        ax.set_ylim(0, 2)
        ax.set_xlabel(r"Bloch Wave Vector $\beta$")
        ax.set_ylabel(r"Frequency [$\frac{a \omega}{2\pi c}$]")
        ax.grid(True)
        plt.show()
