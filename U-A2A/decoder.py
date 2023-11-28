import torch
import torch.nn as nn
import torch.nn.functional as F
import config


class Decoder(nn.Module):
    def __init__(self):
        super(Decoder, self).__init__()
        self.fc = nn.Linear(config.hidden_size, len(config.dict) + len(config.ns))

    def forward(self, encoder_hidden):
        encoder_squeeze = encoder_hidden.squeeze(dim=1)
        output_fc = F.log_softmax(self.fc(encoder_squeeze),
                                  dim=-1)
        return output_fc

    def evaluate_top_n(self, encoder_hidden, N):
        decoder_output_t = self.forward_onestep(encoder_hidden)
        a, idx1 = torch.sort(decoder_output_t[0], descending=True)
        idx = idx1[:N]
        return idx

