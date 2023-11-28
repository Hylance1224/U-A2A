

from encoder import Encoder
from decoder import Decoder
import torch.nn as nn
import torch
import numpy as np


def get_another_features(len = 256):
    arr = []
    arr1 = []
    for i in range(0, len):
        arr.append(20)
    arr1.append(arr)
    arr1 = np.mat(arr1)
    arr1 = torch.from_numpy(arr1)
    emb = nn.Embedding(num_embeddings=30, embedding_dim=3)
    another_features = emb(arr1)
    return another_features


class Seq2Seq(nn.Module):
    def __init__(self):
        super(Seq2Seq, self).__init__()
        self.encoder = Encoder()
        self.decoder = Decoder()

    def forward(self, input, input_length, target):
        encoder_outputs, encoder_hidden, encoder_cell = self.encoder(input, input_length)
        decoder_outputs, decoder_hidden, decoder_cell = self.decoder(encoder_hidden, encoder_cell, target)
        return decoder_outputs, decoder_hidden

    def evaluate(self, input, input_length):
        encoder_outputs, encoder_hidden, encoder_cell = self.encoder(input, input_length)
        decoder_outputs, decoder_predict = self.decoder.evaluate(encoder_hidden, encoder_cell)
        return decoder_predict[0]
