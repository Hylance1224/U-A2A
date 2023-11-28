from seq2seq import Seq2Seq
from torch.optim import Adam
from tqdm import tqdm
import os
import dataset
import config
import torch.nn.functional as F
import torch
import numpy as np
import matplotlib.pyplot as plt



seq2seq_model = Seq2Seq().to(config.device)
optimizer = Adam(seq2seq_model.parameters(), lr=0.001)
if os.path.exists('./model/seq2seq_model.pkl'):
    seq2seq_model.load_state_dict(torch.load('./model/seq2seq_model.pkl'))
    optimizer.load_state_dict(torch.load('./model/seq2seq_optimizer.pkl'))

loss_list = []


def train(epoch):
    data_loader = dataset.get_dataloader(train=True)
    bar = tqdm(data_loader, total=len(data_loader), ascii=True, desc='train')
    for idx, (input, target, input_length, target_length) in enumerate(bar):
        input = input.to(config.device)
        target = target.to(config.device)

        input_length = input_length.to(config.device)

        decoder_ouputs, _ = seq2seq_model(input, input_length, target)

        decoder_ouputs = decoder_ouputs.view(-1, len(config.dict) + len(config.ns))

        target = target.view(-1)
        loss = F.nll_loss(decoder_ouputs, target, ignore_index=config.ns.PAD)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        loss_list.append(loss.item())

        bar.set_description("epoch:{} idx:{} loss:{:.3f}".format(epoch, idx, np.mean(loss_list)))
        if not (idx % 100):
            torch.save(seq2seq_model.state_dict(), './model/seq2seq_model.pkl')
            torch.save(optimizer.state_dict(), './model/seq2seq_optimizer.pkl')


if __name__ == '__main__':
    for i in range(100):
        train(i)

    plt.figure(figsize=(50, 8))
    plt.plot(range(len(loss_list)), loss_list)
    plt.show()
