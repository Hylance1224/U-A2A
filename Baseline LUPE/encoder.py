import torch.nn as nn
import config
from torch.nn.utils.rnn import pack_padded_sequence,pad_packed_sequence

class Encoder(nn.Module):
    def __init__(self):
        super(Encoder,self).__init__()
        self.emb = nn.Embedding(num_embeddings=len(config.dict) + len(config.ns),embedding_dim=config.embedding_dim,padding_idx=config.ns.PAD)
        self.gru = nn.LSTM(input_size=config.embedding_dim,hidden_size=config.hidden_size,num_layers=config.num_layers,batch_first=True)


    def forward(self,input,input_length):
        input_embeded = self.emb(input)
        input_packed = pack_padded_sequence(input_embeded,input_length,batch_first=True)
        output,(hidden, cell) = self.gru(input_packed)
        output_paded,output_paded_length = pad_packed_sequence(output,batch_first=True,padding_value=config.Num2Sequence.PAD)
        return output_paded, hidden, cell


if __name__=='__main__':
    import dataset
    data_loader = dataset.get_dataloader()
    encoder = Encoder()
    for input,target,input_length,target_length in data_loader:
        encoder_outputs,encoder_hidden = encoder(input,input_length)
        print(encoder_outputs.size())
        print(encoder_hidden.size())
        break
