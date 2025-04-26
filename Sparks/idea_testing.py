#!/usr/bin/env python
# coding: utf-8

coder_1_system_message = '''You are an expert in Python coding. You carefully write the code.'''

coder_1_prompt = '''You are given a newly proposed research idea:

{idea}

which was developed to address the following query

{query}

Your task is to consider the query and idea and **write a Python script** that implements this idea using the available toole.
The implementation should lead to the results necessary to test the hypothesis. 

1- In your code:
-All relevant functions are stored in functions.py module. You must import it in your code to use the functions (using from functions import *).
-Do not create new folders; save all files in the current directory.
-Save all individual per sample results in results.json to enable traceability and debugging.
-Save all final outputs (averages, std, etc) to final_results.json.
-Document the workflow in notes.txt

IMPORTANT NOTE: 
- The difference between per sample results and final results is that, final results include only the values that we need to validate and test the hypothesis. Whereas, results include every per sample result that we have for instance by calling tools.
- Often, statistical averages are involved to obtain the final results. To ensure reproducability, include those parameter values that were used to find the statistical averages in final results.
e.g.         "Fmax": {{
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

2- In notes.txt, include the following:
-A detailed and verbose description of the research idea.
-A comprehensive explanation of the steps taken in this implementation.
-A clear, step-by-step workflow used to implement the idea.
-A list of the tools utilized, along with the input parameters provided to each tool.
-A summary of what was achieved during this implementation.
-To support reproducibility, include a sample output dictionary (with keys and representative values) as stored in results.json.
-At the begenning of notes mention Timestamp XXX. Then include "Initial implementation: <write what is the objective of this implementation>"
-In between, append and document verbose, detailed document.
-At the end, write "End of Initial implementation Documentation."

3- OUTPUT FILES:
The code should generate and return the following output files:
-results.json
-final_results.json
-notes.txt

IMPORTANT:
-results.json and final_results.json will be used later for subsequent results analysis and hypothesis validation. So, make sure they are available.
-notes.txt will be used later for write-up, so be as comprehensive as possible and document all the details.

4- In case you want to generate plots:
-Do not use plt.show() — use plt.savefig() instead.
-Name your plots descriptively.
-Label axes clearly and meaningfully.
-If averaging is involved, include all data points in your plots.
-Create as many plots as needed to illustrate results clearly.

5-When implementing the idea, think of the following key factors regarding sample numbers:
-Statistical Significance
-System Variability
-Confidence and Error Estimation
-Sampling Strategy
-Computational or Experimental Cost

6- Available tools:
The functions that you have access to are as follows (available in functions.py module)
{tools}

7- Using tools:
-When using tools, always check the output first. If results exist and are not None, they should be used. Otherwise, errors may occur.

Note that your implementation you should account for the following constraints:
{constraints}

RESPONSE FORMAT:
Provide your response in the following format:

<code_START>
<CODE>
<code_FINISH>

Replace <CODE> with your complete and well-organized Python script. 

Additional note:
Write just the raw Python logic, no Markdown formatting, and no main() function wrapper, no ```python in the beginning and ``` in the end.
'''


coder_2_prompt = '''
Carefully examine the Python script that was generated to implement the research idea.

Your goal is to evaluate the code for:
- **Correctness**: Does it correctly implement the proposed research idea using the available tools?
- **Reproducibility**: Are all necessary outputs saved, and is the workflow documented thoroughly for future reuse?
- **Documentation**: Is `notes.txt` clearly written, including all relevant details such as the research goal, steps taken, tools used, parameters, and sample outputs?

**Specifically check the following:**
- All tool outputs are checked for validity (i.e., not None) before being used.
- All results, including intermediate ones, are saved in `results.json` and `final_results.json`.
- The workflow is comprehensively logged in `notes.txt`, with any additional helpful information that could facilitate future write-ups.
- The appropriate functions from `functions.py` are correctly used.
- No new folders are created; all outputs are stored in the current working directory.

- If the original code satisfies **all requirements**, return it unchanged.
- If you identify any issues, gaps, or opportunities for improvement, revise the code accordingly.

Provide your response in the following format:

THOUGHT  
<THOUGHT>

In <THOUGHT>, provide your feedback and reasoning about the code's strengths and any required improvements.

<code_START>  
<CODE>  
<code_FINISH>  

In <CODE>, provide the complete final version of the Python script. 

Additional note:
Write just the raw Python logic, no Markdown formatting, and no main() function wrapper, no ```python in the beginning and ``` in the end.
'''