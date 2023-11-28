import torch.nn as nn
import config
from torch.nn.utils.rnn import pack_padded_sequence,pad_packed_sequence

class Encoder(nn.Module):
    def __init__(self):
        super(Encoder,self).__init__()
        self.gru = nn.GRU(input_size=config.embedding_dim,hidden_size=config.hidden_size,num_layers=config.num_layers,batch_first=True)

    def forward(self,input,input_length):
        input_embeded = self.emb(input)
        input_packed = pack_padded_sequence(input_embeded,input_length,batch_first=True)
        output,hidden = self.gru(input_packed)
        output_paded,output_paded_length = pad_packed_sequence(output,batch_first=True,padding_value=config.Num2Sequence.PAD)
        return output_paded,hidden