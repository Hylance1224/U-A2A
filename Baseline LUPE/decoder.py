import torch
import torch.nn as nn
import torch.nn.functional as F
import config
import numpy as np
import random


class Decoder(nn.Module):
    def __init__(self):
        super(Decoder, self).__init__()
        self.emb = nn.Embedding(num_embeddings=len(config.dict) + len(config.ns), embedding_dim=config.embedding_dim,
                                padding_idx=config.ns.PAD)
        self.gru = nn.LSTM(input_size=config.embedding_dim, hidden_size=config.hidden_size, num_layers=config.num_layers,
                          batch_first=True)
        self.fc = nn.Linear(config.hidden_size, len(config.dict) + len(config.ns))

    def forward(self, encoder_hidden, encoder_cell, target):
        decoder_hidden = encoder_hidden
        decoder_cell = encoder_cell
        batch_size = encoder_hidden.size(1)
        decoder_input = torch.LongTensor([[config.ns.SOS]] * batch_size).to(config.device)

        decoder_outputs = torch.zeros([batch_size, config.testing_len, len(config.dict) + len(config.ns)]).to(config.device)


        for t in range(config.testing_len):
            decoder_output_t, decoder_hidden, decoder_cell = self.forward_onestep(decoder_input,
                                                                    decoder_hidden,
                                                                    decoder_cell)

            decoder_outputs[:, t, :] = decoder_output_t

            use_teacher_forcing = random.random() > 0.5
            if use_teacher_forcing:
                decoder_input = target[:, t].unsqueeze(1)
            else:
                value, index = decoder_output_t.max(dim=-1)
                decoder_input = index.unsqueeze(dim=-1)
        return decoder_outputs, decoder_hidden, decoder_cell

    def forward_onestep(self, decoder_input, pre_decoder_hidden, pre_decoder_cell):
        decoder_input_embeded = self.emb(decoder_input)
        output, (decoder_hidden, decoder_cell) = self.gru(decoder_input_embeded,
                                                          (pre_decoder_hidden, pre_decoder_cell))
        output_squeeze = output.squeeze(dim=1)
        output_fc = F.log_softmax(self.fc(output_squeeze),
                                  dim=-1)
        return output_fc, decoder_hidden, decoder_cell

    def evaluate(self, encoder_hidden, encoder_cell):
        decoder_hidden = encoder_hidden
        decoder_cell = encoder_cell
        batch_size = encoder_hidden.size(1)
        decoder_input = torch.LongTensor([[config.ns.SOS]] * batch_size).to(config.device)
        decoder_outputs = torch.zeros([batch_size, config.testing_len, len(config.dict) + len(config.ns)]).to(
            config.device)
        decoder_predict = []

        for t in range(config.testing_len):
            decoder_output_t, decoder_hidden, decoder_cell = \
                self.forward_onestep(decoder_input, decoder_hidden, decoder_cell)
            decoder_outputs[:, t, :] = decoder_output_t
            value, index = decoder_output_t.max(dim=-1)
            decoder_input = index.unsqueeze(dim=-1)
            decoder_predict.append(
                index.cpu().detach().numpy())

        decoder_predict = np.array(decoder_predict).transpose()
        return decoder_outputs, decoder_predict




