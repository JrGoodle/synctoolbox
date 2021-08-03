import librosa
from libfmp.c6 import compute_local_average
import numpy as np


def spectral_flux(f_audio: np.ndarray,
                  Fs: int = 22050,
                  feature_rate: int = 50,
                  gamma: float = 10,
                  M_sec: float = 0.1) -> np.ndarray:
    """Generates the spectral-based novelty curve given an audio array.

    This function is based on the FMP notebook on "Spectral-Based Novelty":
    https://www.audiolabs-erlangen.de/resources/MIR/FMP/C6/C6S1_NoveltySpectral.html

    Parameters
    ----------
    f_audio : np.ndarray
        One dimensional f_audio array (mono)

    Fs : float
        Sampling rate of ``f_audio`` (in Hz)

    feature_rate : int
        Features per second

    gamma : float
        Log compression factor

    M_sec: float
        Determines size (2M+1) in samples of centric window  used for local average

    Returns
    -------
    nov_norm : np.ndarray [shape=(N, )]
        Enhanced novelty curve with the subtraction of a local average
    """

    window_size = int(Fs / feature_rate * 2)
    hop_size = int(window_size / 2)

    X = librosa.stft(f_audio,
                     n_fft=window_size,
                     hop_length=hop_size,
                     win_length=window_size,
                     window='hanning')

    Y = np.log(1 + gamma * np.abs(X))
    Y_diff = np.diff(Y, n=1)

    # Half wave rectification
    Y_diff[Y_diff < 0] = 0

    # Novelty curve
    nov = np.sum(Y_diff, axis=0)

    # Compute local average
    M = int(np.ceil(M_sec * Fs / hop_size))
    local_average = compute_local_average(nov, M)

    # Subtract the local average from the novelty curve
    nov_norm = nov - local_average
    nov_norm[nov_norm < 0] = 0
    nov_norm = nov_norm / max(nov_norm)

    return nov_norm
