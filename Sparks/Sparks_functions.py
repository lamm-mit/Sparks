#!/usr/bin/env python
# coding: utf-8

import json
import shutil
import os
from idea_generation import *
from idea_testing import *
from refinement import *
from documentation import *
from Sparks_utils import *
from pathlib import Path
import sys

sys.path.append('../Sparks')

base_dir = Path(os.environ["PROJECT_DIR"])

def generate_idea(query, tools, constraints):

    msg_history_idea_1 = []

    prompt = scientist_1_prompt.format(
            query=query,
            tools=tools,
            constraints=constraints,  
        )
    
    print(f"Generating new idea")


    text_idea_1, msg_history_idea_1 = get_response_from_llm(
        system_message=scientis_1_system_message,
        prompt= prompt,
        model='o3',
        temperature=1,
        reasoning_effort='high',
        msg_history=msg_history_idea_1,
        print_debug=False,
    )
    
    text_idea_2, msg_history_idea_1 = get_response_from_llm(
        system_message=scientis_2_system_message,
        prompt= scientis_2_prompt.format(
            query=query,
            tools=tools,
            constraints=constraints,  
        ),
        model='o3',
        temperature=1,
        reasoning_effort='high',
        msg_history=msg_history_idea_1,
    )

    json_output_idea_1 = extract_json_between_markers(text_idea_2)
    
        
    with open(osp.join(base_dir, f"hypothesis.json"), "w") as f:
        json.dump(json_output_idea_1, f, indent=4)
    
    with open(osp.join(base_dir, f"hypothesis_chat.json"), "w") as f:
        json.dump(msg_history_idea_1, f, indent=4)

    with open(osp.join(base_dir, f"hypothesis.json"), "r") as f:
        new_hypothesis = json.load(f)
    
    print(f'Idea generated:\n{new_hypothesis}')


def test_idea(query, tools, constraints):
    msg_history_code_3 = []

    with open(osp.join(base_dir, f"hypothesis.json"), "r") as f:
        new_hypothesis = json.load(f)


    print(f'Generating implementation code')


    text_code_3, msg_history_code_3 = get_response_from_llm(
        system_message=coder_1_system_message,
        prompt=coder_1_prompt.format(
            idea=new_hypothesis,
            query=query,
            tools=tools,
            constraints=constraints,
        ),
        model='o3-mini',
        reasoning_effort='high',
        temperature=1,
        msg_history=msg_history_code_3,
        print_debug=False
    )

    text_code_3, msg_history_code_3 = get_response_from_llm(
        system_message=coder_1_system_message,
        prompt=coder_2_prompt.format(
        ),
        model='gpt-4.1',
        reasoning_effort='high',
        msg_history=msg_history_code_3,
        print_debug=False
    )

    with open(osp.join(base_dir, f"ImplementationCode_round_1.json"), "w") as f:
        json.dump(text_code_3, f, indent=4)
        
    with open(osp.join(base_dir, f"ImplementationCode_round_1_chat.json"), "w") as f:
        json.dump(msg_history_code_3, f, indent=4)
    
    with open(osp.join(base_dir, f"ImplementationCode_round_1.json"), "r") as f:
        code_text = json.load(f)


####################################################################################

import os.path as osp
import re
import subprocess


def initial_implementation():

    # Load code block from JSON
    code_path = osp.join(base_dir, "ImplementationCode_round_1.json")
    with open(code_path, "r") as f:
        code_text = json.load(f)

    match = re.search(r'<code_START>(.*?)<code_FINISH>', code_text, re.DOTALL)
    if match:
        code_block = match.group(1).strip()
        print('Implementation code generated.')
    else:
        print("Code block not found.")
        return

    # Write code to file inside base_dir
    script_path = osp.join(base_dir, "experiment_idea_1.py")
    with open(script_path, 'w') as f:
        f.write(code_block)

    # Execute the script from base_dir
    print('Executing the code Round 1...')
    result = subprocess.run(
        ['python', script_path],
        stderr=subprocess.PIPE,
        cwd=base_dir,
        text=True
    )

    # Save results based on execution outcome
    result_file = osp.join(base_dir, "results_verbose_round_1.json")
    if result.returncode == 0:
        print('Implementation code executed successfully!')
        with open(result_file, "w") as f:
            json.dump('', f, indent=4)
    else:
        print('Error in execution!')
        with open(result_file, "w") as f:
            json.dump(result.stderr[-1000:], f, indent=4)

        print(result.stderr[-1000:])


        
def refine_approach(query, constraints, total_followup_rounds):
    
    #last_exp_round = 1

    for follow_round in range(2, total_followup_rounds+2):  

        with open(osp.join(base_dir, f"results_verbose_round_{follow_round-1}.json"), "r") as f:
            error = json.load(f) 
            
        with open(osp.join(base_dir, f"hypothesis.json"), "r") as f:
            new_hypothesis = json.load(f)
            
        with open (osp.join(base_dir, f'notes.txt'), "r") as f:
            notes= f.read()    
            
        with open (osp.join(base_dir, f'final_results.json'), "r") as f:
            final_results= json.load(f)
    
        with open (osp.join(base_dir, f'results.json'), "r") as f:
            results= json.load(f)
    
        with open (osp.join(base_dir, f'experiment_idea_{follow_round-1}.py'), "r") as f:
            code= f.read()    
            
        msg_history_code_2 = []
    
        print(f"Generating followup code round {follow_round-1}")
    
        text_code_2, msg_history_code_2 = get_response_from_llm(
            system_message=refiner_1_system_message,
            prompt=refiner_1_prompt.format(
                query=query,
                idea=new_hypothesis,
                notes=notes,
                results=str(results)[:1500],
                final_results=final_results,
                code=code,
                error=error,
                total_rounds=total_followup_rounds,
                current_round=f'{follow_round-1}',
                constraints=constraints,
            ),
            model='o3',
            reasoning_effort='high',
            temperature=1,
            msg_history=msg_history_code_2,
            print_debug=False
        )
    
        text_code_2, msg_history_code_2 = get_response_from_llm(
            system_message=refiner_1_system_message,
            prompt=refiner_2_prompt.format(
            ),
            model='gpt-4.1',
            reasoning_effort='high',
            temperature=0,
            msg_history=msg_history_code_2,
            print_debug=False
        )
    
        with open(osp.join(base_dir, f"ImplementationCode_round_{follow_round}.json"), "w") as f:
            json.dump(text_code_2, f, indent=4)
            
        with open(osp.join(base_dir, f"ImplementationCode_round_{follow_round}_chat.json"), "w") as f:
            json.dump(msg_history_code_2, f, indent=4)
        
        with open(osp.join(base_dir, f"ImplementationCode_round_{follow_round}.json"), "r") as f:
            code_text = json.load(f)
    
        thought_match = re.search(r'THOUGHT:(.*?)<code_START>', code_text, re.DOTALL)
        thought = thought_match.group(1).strip()
        
        print(thought)
        
        match = re.search(r'<code_START>(.*?)<code_FINISH>', code_text, re.DOTALL)
        if match:
            code_block = match.group(1).strip()
        else:
            print("Code block not found.")
    
        if "NO_FOLLOWUP" in code_block:
            last_exp_round = follow_round-1
            break
      
        script_path = osp.join(base_dir, f"experiment_idea_{follow_round}.py")
        with open(script_path, 'w') as f:
            f.write(code_block)
        print(f'Executing the code follow-up Round {follow_round-1}...')

        result_follow = subprocess.run(
            ['python', script_path],
            stderr=subprocess.PIPE,
            cwd=base_dir,
            text=True
        )

        # Save results based on execution outcome
        result_file = osp.join(base_dir, f"results_verbose_round_{follow_round}.json")
        if result_follow.returncode == 0:
            print('Implementation code executed successfully!')
            last_exp_round = follow_round
            with open(result_file, "w") as f:
                json.dump('', f, indent=4)
        else:
            print('Error in execution!')
            last_exp_round = follow_round - 1
            with open(result_file, "w") as f:
                json.dump(result_follow.stderr[-1000:], f, indent=4)

            print(result_follow.stderr[-1000:])
    
    return last_exp_round


    #### PLOTTTTING THE RESULTS
    
def create_reason_plots(query, last_exp_round):

    print('Designing the plots')

    msg_history_code_4 = []
    
    with open (osp.join(base_dir, f"hypothesis.json"), "r") as f:
        new_hypothesis= json.load(f)    
        
    with open (osp.join(base_dir, f'notes.txt'), "r") as f:
        notes= f.read()    
    
    with open (osp.join(base_dir, f'final_results.json'), "r") as f:
        final_results= json.load(f) 
    
    with open (osp.join(base_dir, f'results.json'), "r") as f:
        results= json.load(f) 
    
    with open (osp.join(base_dir, f'experiment_idea_{last_exp_round}.py'), "r") as f:
        code= f.read()    
        
    #idea = 'idea: '+ new_hypothesis['idea'] + '\nhypothesis: '+ new_hypothesis['hypothesis']
    idea = new_hypothesis
    
    text_code_4, msg_history_code_4 = get_response_from_llm(
        system_message=coder_plot_1_message,
        prompt=coder_plot_1_prompt.format(
            query=query,
            idea=idea,
            notes=notes,
            code=code,
            final_results=final_results,
            results=str(results)[:1500], 
        ),
        model='o3-mini',
        temperature=1,
        reasoning_effort='high',
        msg_history=msg_history_code_4,
        print_debug=False
    )
    
    text_code_4, msg_history_code_4 = get_response_from_llm(
        system_message=coder_plot_1_message,
        prompt=coder_plot_2_prompt.format(
        ),
        model='o3-mini',
        temperature=1,
        reasoning_effort='high',
        msg_history=msg_history_code_4,
        print_debug=False
    )
    
    with open(osp.join(base_dir, f"CodePlots_chat.json"), "w") as f:
        json.dump(msg_history_code_4, f, indent=4)
    
    with open(osp.join(base_dir, f"CodePlots.json"), "w") as f:
        json.dump(text_code_4, f, indent=4)
    
    with open(osp.join(base_dir, f"CodePlots.json"), "r") as f:
        text_code_4 = json.load(f)
    
    match = re.search(r'<code_START>(.*?)<code_FINISH>', text_code_4, re.DOTALL)
    
    if match:
        code_block = match.group(1).strip()
    else:
        print("Code block not found.")


    script_path = osp.join(base_dir, f"plots.py")
    with open(script_path, 'w') as f:
        f.write(code_block)
    print(f'Creating the plots...')

    result = subprocess.run(
        ['python', script_path],
        cwd=base_dir,
        capture_output=True,
        text=True
    )

    
    if result.returncode==1:
        error = result.stderr
        print(f'An error occured!\n{error}') 
        print('Re-generating the plots')
        
        with open(f"plots.py", 'r') as f:
            code_plot = f.read()
            
        msg_history_code_4 = []
            
        text_code_4_fix, msg_history_code_4 = get_response_from_llm(
        system_message=coder_plot_1_message,
        prompt=coder_plot_fix_prompt.format(
            query=query,
            idea=idea,
            notes=notes,
            code=code_plot,
            error=str(error)
        ),
        model='o3-mini',
        temperature=1,
        reasoning_effort='high',
        msg_history=msg_history_code_4,
        print_debug=False
        )
    
        match = re.search(r'<code_START>(.*?)<code_FINISH>', text_code_4_fix, re.DOTALL)
        if match:
            code_block = match.group(1).strip()
        else:
            print("Code block not found.")

        script_path = osp.join(base_dir, f"plots.py")
        with open(script_path, 'w') as f:
            f.write(code_block)
        print(f'Creating the plots...')

        result = subprocess.run(
            ['python', script_path],
            cwd=base_dir,
            capture_output=True,
            text=True
        )

        cleaned_output = result.stdout 
        
        with open(osp.join(base_dir, f"plots.json"), "w") as f:
            json.dump(cleaned_output, f, indent=4)
    
    else:
    
        print('Plots generated!')
        cleaned_output = result.stdout 
        
        with open(osp.join(base_dir, f"plots.json"), "w") as f:
            json.dump(cleaned_output, f, indent=4)


def create_introduction(query):

    print('Writing Introduction...')

    msg_history_report_1 = []
    
    with open(osp.join(base_dir, f"hypothesis_chat.json"), "r") as f:
        new_hypothesis_chat = json.load(f)
    
    text_report_1, msg_history_report_1 = get_response_from_llm(
        system_message=writer_system_message,
        prompt=writer_introduction_prompt.format(
            query=query,
            idea=new_hypothesis_chat,
        ),
        model='o3',
        temperature=1,
        reasoning_effort='high',
        msg_history=msg_history_report_1,
        print_debug=False
    )
    
    text_report_1, msg_history_report_1 = get_response_from_llm(
        system_message=writer_system_message,
        prompt=writer_reflection_prompt.format(
        ),
        model='gpt-4.1',
        reasoning_effort='high',
        temperature=0.5,
        msg_history=msg_history_report_1,
        print_debug=False
    )
    
    with open(osp.join(base_dir, f"TextReport_1_chat.json"), "w") as f:
        json.dump(msg_history_report_1, f, indent=4)
    
    with open(osp.join(base_dir, f"TextReport_1.json"), "w") as f:
        json.dump(text_report_1, f, indent=4)
    
    with open(osp.join(base_dir, f"TextReport_1.json"), "r") as f:
        text_report_1 = json.load(f)
    
    match = re.search(r'<tex_START>(.*?)<tex_FINISH>', text_report_1, re.DOTALL)
    
    if match:
        code_block_1 = match.group(1).strip()
        print('latex generated')
    else:
        print("Code block not found.")
        
    with open(osp.join(base_dir, f'introduction.tex'), 'w') as f:
        f.writelines(code_block_1)

def create_methods(query, tools, constraints, last_exp_round,):
    print('Writing Methods...')
    
    msg_history_report_2 = []
    
    with open(osp.join(base_dir, f'introduction.tex'), 'r') as f:
        text = f.read()
        
    with open (osp.join(base_dir, f'notes.txt'), 'r') as f:
        notes= f.read()    
    
    with open (osp.join(base_dir, f'experiment_idea_{last_exp_round}.py'), 'r') as f:
        code= f.read()  
    
    text_report_2, msg_history_report_2 = get_response_from_llm(
        system_message=writer_system_message,
        prompt=writer_methods_prompt.format(
            document=text,
            code=code,
            notes=notes,
            tools=tools,
            constraints=constraints,
        ),
        model='o3',
        temperature=1,
        reasoning_effort='high',
        msg_history=msg_history_report_2,
        print_debug=False
    )
    
    text_report_2, msg_history_report_2 = get_response_from_llm(
        system_message=writer_system_message,
        prompt=writer_reflection_prompt.format(
        ),
        model='gpt-4.1',
        reasoning_effort='high',
        temperature=0.5,
        msg_history=msg_history_report_2,
        print_debug=False
    )
    
    with open(osp.join(base_dir, f"TextReport_2_chat.json"), "w") as f:
        json.dump(msg_history_report_2, f, indent=4)
    
    with open(osp.join(base_dir, f"TextReport_2.json"), "w") as f:
        json.dump(text_report_2, f, indent=4)
    
    with open(osp.join(base_dir, f"TextReport_2.json"), "r") as f:
        text_report_2 = json.load(f)
    
    match = re.search(r'<tex_START>(.*?)<tex_FINISH>', text_report_2, re.DOTALL)
    
    if match:
        code_block_2 = match.group(1).strip()
        print('latex generated')
    else:
        print("Code block not found.")
    
    with open(osp.join(base_dir, f'methods.tex'), 'w') as f:
        f.writelines(code_block_2)

def create_results():
    print('Writing Results...')
    
    msg_history_report_3 = []
    
    text = ''
    
    with open(osp.join(base_dir, f'introduction.tex'), 'r') as f:
        intro = f.read()
    
    with open(osp.join(base_dir, f'methods.tex'), 'r') as f:
        methods = f.read()
    
    text += intro
    text += '\n'
    text += methods
    
    with open(osp.join(base_dir, f'notes.txt'), "r") as f:
        notes= f.read()     
    
    with open(osp.join(base_dir, f"plots.json"), "r") as f:
        plots = json.load(f)
    
    with open(osp.join(base_dir, f"final_results.json"), "r") as f:
        final_results = json.load(f)
    
    try:
        with open(osp.join(base_dir, f"fit_parameters.json"), "r") as f:
            fit_parameters = json.load(f)
    except FileNotFoundError:
        fit_parameters = ''
    except json.JSONDecodeError:
        fit_parameters = ''
        
    text_report_3, msg_history_report_3 = get_response_from_llm(
        system_message=writer_system_message,
        prompt=writer_results_prompt.format(
            document=text,
            notes=notes,
            plots=plots,
            regression=fit_parameters,
            final_results=final_results,
        ),
        model='o3',
        temperature=1,
        reasoning_effort='high',
        msg_history=msg_history_report_3,
        print_debug=False
    )
    
    text_report_3, msg_history_report_3 = get_response_from_llm(
        system_message=writer_system_message,
        prompt=writer_reflection_prompt.format(
        ),
        model='gpt-4.1',
        reasoning_effort='high',
        temperature=0.5,
        msg_history=msg_history_report_3,
        print_debug=False
    )
    
    
    with open(osp.join(base_dir, f"TextReport_3_chat.json"), "w") as f:
        json.dump(msg_history_report_3, f, indent=4)
    
    with open(osp.join(base_dir, f"TextReport_3.json"), "w") as f:
        json.dump(text_report_3, f, indent=4)
    
    with open(osp.join(base_dir, f"TextReport_3.json"), "r") as f:
        text_report_3 = json.load(f)
        
    match = re.search(r'<tex_START>(.*?)<tex_FINISH>', text_report_3, re.DOTALL)
    
    if match:
        code_block_3 = match.group(1).strip()
        print('latex generated')
    else:
        print("Code block not found.")
    
    with open(osp.join(base_dir, f'results.tex'), 'w') as f:
        f.writelines(code_block_3)

def create_conclusion(query,):

    print('Writing Conclusion...')

    msg_history_report_4 = []
    
    text = ''
    
    with open(osp.join(base_dir, f'introduction.tex'), 'r') as f:
        intro = f.read()
    
    with open(osp.join(base_dir, f'methods.tex'), 'r') as f:
        methods = f.read()
    
    with open(osp.join(base_dir, f'results.tex'), 'r') as f:
        results = f.read()
    
    text += intro
    text += '\n'
    text += methods
    text += '\n'
    text += results
        
    text_report_4, msg_history_report_4 = get_response_from_llm(
        system_message=writer_system_message,
        prompt=writer_conclusion_prompt.format(
            query=query,
            document=text,
        ),
        model='o3',
        temperature=1,
        reasoning_effort='high',
        msg_history=msg_history_report_4,
        print_debug=False
    )
    
    text_report_4, msg_history_report_4 = get_response_from_llm(
        system_message=writer_system_message,
        prompt=writer_reflection_prompt.format(
        ),
        model='gpt-4.1',
        reasoning_effort='high',
        temperature=0.5,
        msg_history=msg_history_report_4,
        print_debug=False
    )
    
    
    with open(osp.join(base_dir, f"TextReport_4_chat.json"), "w") as f:
        json.dump(msg_history_report_4, f, indent=4)
    
    with open(osp.join(base_dir, f"TextReport_4.json"), "w") as f:
        json.dump(text_report_4, f, indent=4)
    
    with open(osp.join(base_dir, f"TextReport_4.json"), "r") as f:
        text_report_4 = json.load(f)
    
    match = re.search(r'<tex_START>(.*?)<tex_FINISH>', text_report_4, re.DOTALL)
    
    if match:
        code_block_4 = match.group(1).strip()
        print('latex generated')
    else:
        print("Code block not found.")


    # Extract the title (including possible newlines inside the curly braces)
    title_match = re.search(r'(\\title\{(?:[^{}]|\{[^{}]*\})*\})', code_block_4, re.DOTALL)
    title_tex = title_match.group(1) if title_match else ''
    
    # Extract everything from \section{Introduction} onwards (the introduction)
    conc_match = re.search(r'(\\section\{Conclusion\}.*)', code_block_4, re.DOTALL)
    conclusion_tex = conc_match.group(1) if conc_match else ''
    
    with open(osp.join(base_dir, f'title.tex'), 'w') as f:
        f.writelines(title_tex)
    
    with open(osp.join(base_dir, f'conclusion.tex'), 'w') as f:
        f.writelines(conclusion_tex)

def create_outlook(query, tools):

    print('Writing Outlook...')

    msg_history_report_5 = []
    
    text = ''
    
    with open(osp.join(base_dir, f'introduction.tex'), 'r') as f:
        intro = f.read()
    
    with open(osp.join(base_dir, f'methods.tex'), 'r') as f:
        methods = f.read()
    
    with open(osp.join(base_dir, f'results.tex'), 'r') as f:
        results = f.read()
    
    with open(osp.join(base_dir, f'conclusion.tex'), 'r') as f:
        conclusion = f.read()
    
    text += intro
    text += methods
    text += results
    text += conclusion
        
    text_report_5, msg_history_report_5 = get_response_from_llm(
        system_message=writer_system_message,
        prompt=writer_outlook_prompt.format(
            query=query,
            document=text,
            tools=tools,
        ),
        model='o3',
        temperature=1,
        reasoning_effort='high',
        msg_history=msg_history_report_5,
        print_debug=False
    )
    
    text_report_5, msg_history_report_5 = get_response_from_llm(
        system_message=writer_system_message,
        prompt=writer_reflection_prompt.format(
        ),
        model='gpt-4.1',
        reasoning_effort='high',
        temperature=0.5,
        msg_history=msg_history_report_5,
        print_debug=False
    )
    
    with open(osp.join(base_dir, f"TextReport_5_chat.json"), "w") as f:
        json.dump(msg_history_report_5, f, indent=4)
    
    with open(osp.join(base_dir, f"TextReport_5.json"), "w") as f:
        json.dump(text_report_5, f, indent=4)
    
    with open(osp.join(base_dir, f"TextReport_5.json"), "r") as f:
        text_report_5 = json.load(f)
    
    match = re.search(r'<tex_START>(.*?)<tex_FINISH>', text_report_5, re.DOTALL)
    
    if match:
        code_block_5 = match.group(1).strip()
        print('latex generated')
    else:
        print("Code block not found.")
    
    with open(osp.join(base_dir, f'outlook.tex'), 'w') as f:
        f.writelines(code_block_5)

def create_pdf():
    for _ in range(2):
        tex_file = os.path.join(base_dir, f"document.tex")
        
        with open(tex_file, "w", encoding="utf-8") as f:
            f.write(latex_content.format(title="{"+f"title"+"}",
                                        introduction="{"+f"introduction"+"}",
                                         methods="{"+f"methods"+"}",
                                         results="{"+f"results"+"}",
                                         conclusion="{"+f"conclusion"+"}",
                                         outlook="{"+f"outlook"+"}",
                                        )
                   )

        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", f"document.tex"],
            cwd=base_dir,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )



