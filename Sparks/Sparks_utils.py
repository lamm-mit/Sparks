#!/usr/bin/env python
# coding: utf-8

import re
from openai import OpenAI
import json
import os.path as osp
import subprocess

client = OpenAI(organization ='')

#Adopted from AI-Scientist
def extract_json_between_markers(llm_output):
    # Regular expression pattern to find JSON content between ```json and ```
    json_pattern = r"```json(.*?)```"
    matches = re.findall(json_pattern, llm_output, re.DOTALL)

    if not matches:
        # Fallback: Try to find any JSON-like content in the output
        json_pattern = r"\{.*?\}"
        matches = re.findall(json_pattern, llm_output, re.DOTALL)

    for json_string in matches:
        json_string = json_string.strip()
        try:
            parsed_json = json.loads(json_string)
            return parsed_json
        except json.JSONDecodeError:
            # Attempt to fix common JSON issues
            try:
                # Remove invalid control characters
                json_string_clean = re.sub(r"[\x00-\x1F\x7F]", "", json_string)
                parsed_json = json.loads(json_string_clean)
                return parsed_json
            except json.JSONDecodeError:
                continue  # Try next match

    return None  # No valid JSON found


def token_usage(response):
    dic = {"prompt tokens": response.usage.prompt_tokens,
          "completion tokens" : response.usage.completion_tokens,
          "total tokens": response.usage.total_tokens,
           "reasoning tokens": response.usage.completion_tokens_details.reasoning_tokens
          }
    return dic

#Adapted from AI-Scientist
def get_response_from_llm(
        system_message,
        prompt,
        model,
        reasoning_effort="medium",
        print_debug=False,
        msg_history=None,
        temperature=0.75,
        client=client):

    if msg_history is None:
        msg_history = []

    new_msg_history = msg_history + [{"role": "user", "content": prompt}]
    
    if model in ["gpt-4o", "gpt-4-turbo"]:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "developer", "content": system_message},
                *new_msg_history,
            ],
            temperature=temperature,
            max_completion_tokens=15000
        )
        print(token_usage(response))

    elif model in ["gpt-4.1"]:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "developer", "content": system_message},
                *new_msg_history,
            ],
            temperature=temperature,
            max_completion_tokens=20000
        )
        print(token_usage(response))
        
    elif model in ["o1", "o1-mini", "o3", "o3-mini"]:
        response = client.chat.completions.create(
            model=model,
            reasoning_effort=reasoning_effort,
            messages=[
                {"role": "developer", "content": system_message},
                *new_msg_history,
            ],
        )
        print(token_usage(response))
        
    content = response.choices[0].message.content
    new_msg_history = new_msg_history + [{"role": "assistant", "content": content}]

    if print_debug:
        print()
        print("*" * 20 + " LLM START " + "*" * 20)
        for j, msg in enumerate(new_msg_history):
            print(f'{j}, {msg["role"]}: {msg["content"]}')
        print(content)
        print("*" * 21 + " LLM END " + "*" * 21)
        print()

    return content, new_msg_history