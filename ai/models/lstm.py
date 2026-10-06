"""LSTM baseline + GRU challenger (locked arch, T3.1)."""

from __future__ import annotations

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

SEQ_LEN, FEAT_DIM, NCLASS = 45, 189, 50


def build_lstm(nclass: int = NCLASS, seed: int = 7) -> keras.Model:
    keras.utils.set_random_seed(seed)
    inp = keras.Input(shape=(SEQ_LEN, FEAT_DIM), name="landmarks")
    x = layers.Masking(mask_value=0.0)(inp)
    x = layers.LSTM(128, return_sequences=True, dropout=0.3)(x)
    x = layers.LSTM(64)(x)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(64, activation="relu")(x)
    x = layers.Dropout(0.2)(x)
    out = layers.Dense(nclass, activation="softmax")(x)
    model = keras.Model(inp, out, name="SBAI-LSTM-50")
    model.compile(optimizer=keras.optimizers.Adam(1e-3),
                  loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


def build_gru(nclass: int = NCLASS, seed: int = 7) -> keras.Model:
    keras.utils.set_random_seed(seed)
    inp = keras.Input(shape=(SEQ_LEN, FEAT_DIM), name="landmarks")
    x = layers.Masking(mask_value=0.0)(inp)
    x = layers.GRU(128, return_sequences=True, dropout=0.3)(x)
    x = layers.GRU(64)(x)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(64, activation="relu")(x)
    x = layers.Dropout(0.2)(x)
    out = layers.Dense(nclass, activation="softmax")(x)
    model = keras.Model(inp, out, name="SBAI-GRU-50")
    model.compile(optimizer=keras.optimizers.Adam(1e-3),
                  loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model
