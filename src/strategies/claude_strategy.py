import torch
import torch.nn as nn
import pandas as pd
from . import AbstractStrategy, Action
import numpy as np


class ClaudeStrategy(AbstractStrategy):
    def __init__(self, window_size=30):
        self.window_size = window_size
        super().__init__()

        self.model = nn.Sequential(
            nn.Linear(window_size * 5, 32),  # 30 свечей по 5 признаков
            nn.ReLU(),
            nn.Linear(32, 3),
            nn.Softmax(dim=0),
        )

        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.01)

    def action(self, data: pd.DataFrame, position: bool) -> Action:
        df = data.copy()
        # print("HELLO!")
        # print(data)
        sequence = df[len(df) - self.window_size :]
        # print(sequence)

        sequence = sequence[["open", "high", "low", "close", "volume"]].values

        # print(sequence)
        sequence = sequence.reshape((self.window_size * 5,))

        inputs = torch.from_numpy(np.array(sequence)).float()

        outputs = self.model(inputs)
        predictions = outputs.argmax(dim=0)

        action = Action(predictions.item())
        # if action != Action.NONE:
        #     print("wow")
        return action

    def train(self, data: pd.DataFrame):
        sequences = self.get_sequences(data)
        # print(len(sequences))

        inputs = torch.from_numpy(np.array([item[:-1] for item in sequences])).float()
        targets = torch.from_numpy(np.array([item[-1] for item in sequences])).long()
        # print(inputs.shape)
        # print(targets.shape)
        self.optimizer.zero_grad()

        for _ in range(10000):
            outputs = self.model(inputs)
            loss = torch.nn.functional.cross_entropy(outputs, targets)
            print(loss)
            loss.backward()
            self.optimizer.step()

    def get_sequences(self, data):
        df = data.copy()
        # print(data)
        closes = df["close"].values
        diff = np.diff(closes)
        actions = np.where(
            diff > 0,
            Action.LONG.value,
            np.where(diff < 0, Action.SHORT.value, Action.NONE.value),
        )[1:]
        print(actions)
        df = df[:-1]

        sequences = []
        for i in range(len(df) - self.window_size):
            sequence = df[i : i + self.window_size][
                ["open", "high", "low", "close", "volume"]
            ].values.reshape((self.window_size * 5,))
            action = np.array([actions[i]])

            sequence = np.concatenate([sequence, action], axis=0)

            sequences.append(sequence)
        return sequences
