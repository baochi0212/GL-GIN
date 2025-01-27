# -*- coding: utf-8 -*-#

import os, json, random
import numpy as np
import torch
from models.module import ModelManager
from utils.loader import DatasetManager
from utils.process import *
from utils.config import *
# import fitlog

if __name__ == "__main__":
    # fitlog.set_log_dir("logs/")
    # fitlog.add_hyper(args)
    # fitlog.add_hyper_in_file(__file__)
    # Save training and model parameters.
    if not os.path.exists(args.save_dir):
        os.system("mkdir -p " + args.save_dir)

    log_path = os.path.join(args.save_dir, "param.json")
    with open(log_path, "w", encoding="utf8") as fw:
        fw.write(json.dumps(args.__dict__, indent=True))

    # Fix the random seed of package random.
    random.seed(args.random_state)
    np.random.seed(args.random_state)

    # Fix the random seed of Pytorch when using GPU.
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.random_state)
        torch.cuda.manual_seed(args.random_state)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    # Fix the random seed of Pytorch when using CPU.
    torch.manual_seed(args.random_state)
    torch.random.manual_seed(args.random_state)

    # Instantiate a dataset object.
    dataset = DatasetManager(args)
    dataset.quick_build()
    dataset.show_summary()

    # Instantiate a network model object.
    model = ModelManager(
        args, len(dataset.word_alphabet),
        len(dataset.slot_alphabet),
        len(dataset.intent_alphabet)
    )
    model.show_summary()
    # dataloader = dataset.batch_delivery('train')
    # text_batch, slot_batch, intent_batch = next(iter(dataloader))
    # padded_text, [sorted_slot, sorted_intent], seq_lens = dataset.add_padding(
    #        text_batch, [(slot_batch, True), (intent_batch, False)],
    #        digital=True)
    

    # slot_var = torch.LongTensor(sorted_slot)
    # sorted_intent_exp = []
    # for item, num in zip(sorted_intent, seq_lens):
    #     sorted_intent_exp.extend([item] * num)
    # sorted_intent = [multilabel2one_hot(intents, len(dataset.intent_alphabet)) for intents in
    #                              sorted_intent_exp]
    # intent_var = torch.Tensor(sorted_intent)
    # print("???:", slot_var.shape, intent_var.shape)


    # To train and evaluate the models.
    process = Processor(dataset, model, args)
    best_epoch = process.train()
    result = process.validate(
        os.path.join(args.save_dir, "model/model.pkl"),
        dataset,
        args.batch_size, len(dataset.intent_alphabet), args=args)
    print('\nAccepted performance: ' + str(result) + " at test dataset;\n")

    # fitlog.finish()
