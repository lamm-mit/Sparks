#!/usr/bin/env python
# coding: utf-8

refiner_1_system_message = '''You are a strategic scientist trained in scientific research, engineering, and innovation.'''

refiner_1_prompt = """You are given a newly proposed research idea
{idea}

This idea was developed in response to the following scientific query:
{query}

the following Python code was proposed and executed to implement the idea:
{code}

When executing the code, following error was returned (empty if there was no error)
{error}

After code execution, the following files were generated and returned
a- final_results.json: Summarized or final results plus indovidual sampels used for averaging.
b- results.json: Full detailed results per sample.
c- notes.txt: overview of the research idea, detailed explanation of what was done, the workflow, what tool was used with what input parameters, what was achieved.

You can review these files as provided below

{notes}

full or partial preview of final results (excerpt from final_results.json):
{final_results}

full or partial preview of results (excerpt from results.json):
{results}

1- YOUR TASK:
-Your goal is to decide whether follow-up experiments are needed, given the above context, including query, research idea, hypothesis, and results. 
-If follow-up is needed, you must re-plan the current code for further experiments. You have a total of {total_rounds} rounds to re-plan the experiments. You are currently in round {current_round}/{total_rounds}. You are not required to use all the rounds.
-Do not overcomplicate things and re-plan only if required.
-Note that your task is NOT to refine the hypothesis, you merely are tasked to suggest follow-up experiments if needed.

2- The main reasons why follow-up experiments are required are as follows:
-The code did not execute successfully, and errors occurred, resulting in no new results.
-The dataset generated so far for this research idea is insufficient — especially for cases that require robust statistical analysis or a large number of samples for reliable trends.
-Preliminary results showed unexpected or inconclusive behavior, suggesting the need for additional sampling to validate or clarify the findings.
-You may also identify other valid reasons to perform additional experiments based on the context or emerging insights.

3- If follow-up experiments are deemed necessary:
-You must integrate the existing results into your new plan (e.g., by loading final_results.json and results.json in your code).
-In your revised code, you must append the new data to the existing results (results.json) to maintain a unified dataset. This ensures reproducability and the full experimetal history is preserved.
-In your revised code, do not append to final_results.json. Instead, overwrite the final_results.json file with the updated set of final results, which should include both the existing values and the new ones.
e.g. initially the final_results was 
"Fmax": {{
                "median": XXX,
                "CI": [
                    X1,
                    X2
                ],
                "samples": [
                    A,
                    B,
                    C,
                    D,
                    E,
                ]
                }},
After new samples are collected it becomes

 "Fmax": {{
                "median": YYY,
                "CI": [
                    Y1,
                    Y2
                ],
                "samples": [
                    A,
                    B,
                    C,
                    D,
                    E,
                    F,
                    G,
                    H,
                    I,
                    J
                ]
                }},

-In your revised code, you must append the new notes to the existing notes (notes.txt) to maintain a unified documentation and workflow. This file will be used later for write-up, so completeness is crucial.
-To ensure consistentcy, follow the same structure that was used in final_results.json and results.json.
-To ensure uniqueness, the variable names (e.g. for different samples) should not overlap with previous ones.

5- In notes.txt, include the following:
-A detailed and verbose description of the research idea.
-A comprehensive explanation of the steps taken in this follow-up round.
-A clear, step-by-step workflow used to implement the idea.
-A list of the tools utilized, along with the input parameters provided to each tool.
-A summary of what was achieved during this follow-up round.
-To support reproducibility, include a sample output dictionary (with keys and representative values) as stored in results.json.
-At the begenning of notes mention Timestamp XXX. Then include "Follow-up Round {current_round}/{total_rounds}: <write what is the objective of this follow-up>"
-In between, append and document verbose, detailed document.
-At the end, write "End of Follow-up Round {current_round}/{total_rounds} Documentation."

3- OUTPUT FILES:
The code should return the following updated output files:
-results.json
-final_results.json
-notes.txt

6- In results.json:
-Append all the detailed results in json format in "results.json".

7- In final_results.json:
-Append final results in json format in "final_results.json" as described above. 

8- In notes.txt:
- You must update the existing file by appending the new documentation as instructed above.
- Ensure the new results do not overwrite the previous documentation, whereas are appended to them.

9-The following constraints exist and should still be considered in the implementation:
{constraints}

Provide your response in the following format:

THOUGHT:
<THOUGHT>

<code_START>
<CODE>
<code_FINISH>

In <THOUGHT>, explain your reasoning for whether or not to conduct follow-up experiments.

In <CODE>, if no follow-up is necessary, write "NO_FOLLOWUP" within <CODE>. If follow-up is required, in <CODE> provide a clean and well-organized Python script that represents a revised version of the original implementation code.

Do not write ```python in the beginning and ``` in the end of your code.
"""

refiner_2_prompt = '''
Look at the previous discussion and carefully exmaine the decision that was just made.

If follow-up experiments are required:
- check the code for accuracy and completeness. Examine if the right functions have been used. 
- Ensure every single result is saved for reproducability.
- Revise the code if needed. 
- If no revision is required, return the original code.

If no follow-up is required, only return "NO_FOLLOWUP" in the code.

Provide your response in the same format:

THOUGHT:
<THOUGHT>

<code_START>
<CODE>
<code_FINISH>

Do not write ```python in the beginning and ``` in the end of your code.
'''