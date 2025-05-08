#!/usr/bin/env python
# coding: utf-8

import numpy as np
from tqdm.notebook import tqdm
from collections.abc import Iterable
import pandas as pd
import time
import datetime
from matplotlib import pyplot as plt

import torch
from torch.utils.data import Dataset, DataLoader, random_split, RandomSampler, SequentialSampler

def extract_task (string_input, end_task_token=')', shift=0):
    #i=string_input.find(start)
    j=string_input.find(end_task_token)
    return string_input [:j+1+shift]
    
def extract_start_and_end (string_input, start_token='[', end_token=']', ):
    #i=string_input.find(start)
    i=string_input.find(start_token)
    j=string_input.find(end_token)
    return string_input [i+1:j]

# Function to generate output from prompts
def generate_output_from_prompt(model, device, tokenizer, prompt, print_output=False, max_new_tokens=378, 
                            do_sample=True, top_k=500, top_p=0.9, 
                            num_return_sequences=1, 
                            temperature=0.01, num_beams=1):

    model.eval()
    input_ids = torch.tensor(tokenizer.encode(prompt, add_special_tokens = False)).unsqueeze(0)
    input_ids = input_ids.to(device)
    
    sample_outputs = model.generate(
                                input_ids, 
                                #bos_token_id=random.randint(1,30000),
                                #pad_token_id=tokenizer.eos_token_id,
                                eos_token_id =tokenizer.eos_token_id,
                                pad_token_id=tokenizer.eos_token_id,
                                do_sample=do_sample,   
                                top_k=top_k, 
                                #max_length = 700,
                                max_new_tokens=max_new_tokens,
                                top_p=top_p, 
                                num_return_sequences=num_return_sequences,
                                temperature=temperature,
                                num_beams=num_beams,
                                )
    if print_output:
    	for i, sample_output in enumerate(sample_outputs):
        	decoded_txt = tokenizer.decode(sample_output, skip_special_tokens=True)
        	print("{}: {}\n\n".format(i, decoded_txt))
        
    return sample_outputs