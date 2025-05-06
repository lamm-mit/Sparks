#!/usr/bin/env python
# coding: utf-8

coder_plot_1_message = '''You are an scienist trained in scientific research, engineering, and innovation.'''

coder_plot_1_prompt = """The following scientific query has been posed:
{query}

Carefully review the following idea and hypothesis proposed:
{idea}

The following text describes the overview of the research idea, detailed explanation of what was done, the workflow, what tool was used with what input parameters, what was achieved.
{notes}

The following code was executed at the final round
{code}

Final results are stored in and can be loaded from final_results.json. 
Full preview of the final results (excerpt from final_results.json) are as follows:
{results}

More detailed per sample results are stored in results.json.
Partial preview of per sample results (excerpt from results.json) are as follows:
{final_results}

Your TASK:
1- Thoroughly examine the query, idea, workflow, and results
2- Your goal is to design and generate plots that help results analysis, uncover meaningful patterns in the data, and address the scientific query. 
3- In addition to plot generation you should call the image_reasoning function to analyze the image.

The ultimate goal is to use these plots, drive meaningful patterns and correlations, and generate new principle leading to a new discovery.

INSTRUCTIONS:
1) First carefully think what plot types (e.g. line plot, scatter plot, box plot, histogram, etc) are best suited for the problem of interest and represent the results. 
2) You must solely use existing results—no new computations or data generation is allowed.
3) As you can see in the idea and/or code, there might be some plots already proposed/generated. You may regenerate or refine them if you find them insightful.
4) In addition, you may propose new insightful plot types targeting other variable combinations, uncovering other hidden dimensions.
5) As you can see, the results.json file may contain variables and outputs not included in the final_result.json files, mainly because they were not considered as important. You are encouraged to use those variables and parameters in your new plots to unciver other patterns beyond current study.

image_reasoning function:
- In your code, first import the function and prompt via "from functions import image_reasoning, plot_discovery_prompt"
- Then call the function for each image that you have generated 
- Here is the function parameters
-image_reasoning(input_image = 'image.png', prompt=prompt), where 'image.png' is the full name of the image that you generated, and 
prompt=plot_discovery_prompt.format(query={query}, idea={idea})
-image_reasoning returns a dictionary 
- The function returns a string.

### REGRESSION FITS:
- Where applicable, include curve fitting to model trends. Include the R^2 values in the plot legend.
- If a fit is performed, output a table in JSON format (named fit_parameters.json) summarizing the fit parameters, enabling future regeneration of the curve. 
- You must closely examine the data and pick the best regression or fitting model with the lowest R^2 value.

MUSTS:
-In the end, the code SHOULD return (using print command) a dictionary containing the plot names as keys and the plot descriptions as returned by the image_reasoning tool as values. Do not print out anything else. 
-Avoid 3d plots.
-Avoid putting multiple subplots in a same figure.

Provide your response in the following format:

THOUGHT:
<THOUGHT>

<code_START>
<CODE>
<code_FINISH>

In <THOUGHT>, provide your thought on the best plot types that provide valuable insights into the research query and idea and hypothesis and expected outcomes. Also, reason over the different combinations of variables that could be used.

In <CODE>, provide the Python script that creates the new plots. 

Additional note:
Write just the raw Python logic, no Markdown formatting, and no main() function wrapper, no ```python in the beginning and ``` in the end.
"""

coder_plot_2_prompt = """Closely investigate the generated response.

Your TASK:
- Carefully review the previously generated response, especially focusing on code and outputs.
- Assess the Python code for correctness, completeness, and clarity.
- Evaluate all plot types, tables, and variables used:
  - Do the plots effectively convey insights relevant to the problem?
  - Are the variables and visualizations aligned with the research objective?
  - Are the fitting curves properly chosen and the fitting parameters saved to the file (named fit_parameters.json)?
- Consider whether the plots could be improved or more plots could be generated:
  - Propose additional plots if they could enhance interpretation and science discovery.
  - Suggest revisions if the current plots are unclear or incomplete.

- If a revision is needed, return the revised Python script, along with updated code to generate and explain the new plots.
- If no changes are necessary, return the original code as-is.

Respond in the following format:

THOUGHT:
<THOUGHT>

In <THOUGHT>, provide your feedback and assassment, discussing potential issues and ways to improve.

<code_START>
<CODE>
<code_FINISH>

In <CODE>, provide your response.

Additional note:
Write just the raw Python logic, no Markdown formatting, and no main() function wrapper, no ```python in the beginning and ``` in the end.
"""

coder_plot_fix_prompt = """The following scientific query has been posed:
{query}

Carefully review the following idea proposed and its componenets:
{idea}

The following text describes the implementation workflow (read it to understand what has been done so far) 
{notes}

The following code was proposed to plot the results
{code}

However, when executing the code, the following error occured
{error}

Your task is to fix the error and return the corrected code.

Provide your response in the following format:

THOUGHT:
<THOUGHT>

<code_START>
<CODE>
<code_FINISH>

In <THOUGHT>, explain the error and your strategy to fix it.

In <CODE>, provide the corrected Python script. 

Additional note:
Write just the raw Python logic, no Markdown formatting, and no main() function wrapper, no ```python in the beginning and ``` in the end.
"""


latex_content = r"""
\documentclass[onecolumn]{{article}}
\usepackage{{graphicx}} % Required for inserting images
\usepackage{{fancyhdr}}
\usepackage{{geometry}}
\usepackage{{wrapfig}}
\usepackage{{caption}}
\usepackage{{graphicx}}
\usepackage{{amsmath}}
\usepackage{{authblk}}
\usepackage{{setspace}}
\usepackage[most]{{tcolorbox}}
\usepackage{{lipsum}} % for placeholder text

% Define a custom box style
\newtcolorbox{{takeawaybox}}{{
  colback=red!10,       % Background color
  colframe=red!60,      % Border color
  fonttitle=\bfseries,   % Title font
  coltitle=black,        % Title text color
  left=0pt, right=0pt, top=0pt, bottom=0pt, % Padding
  boxrule=0.8pt,         % Border thickness
  arc=2pt,               % Corner roundness
  width=\textwidth,
  before skip=10pt,
  after skip=10pt
}}

 \geometry{{
 a4paper,
 total={{165mm,220mm}},
 left=20mm,
 top=30mm,
 }}


 
\fancyhead{{}}\fancyfoot{{}}
\fancyhead[C]{{In the centre of the header on all pages: \thepage}}

\begin{{document}}
\date{{}}
\input{title}
\author{{AI-generated document}}
\maketitle

% The introduction section of the document.
\input{introduction}

% The methods section of the document
\input{methods}

% The results section of the document.
\input{results}

% The conclusion section of the document.
\input{conclusion}

% The future work section of the document.
\input{outlook}

\end{{document}}
"""

writer_system_message = '''Your are a sophisticated writer with expertise in writing scientific reports and articles.'''

writer_introduction_prompt = """You are given the following scientific query and an innovative research idea designed to address it:

Query:
{query}

Idea:
{idea}

Your TASK:
- Carefully analyze both the query and the idea.
- Write a detailed, structured, and well-reasoned document in **latex format**.

WRITING STRATEGY:
The introduction section should carefully adress the following aspects
-States the problem and its scientific or practical importance.
-Describes the complexity or barriers that make this a non-trivial problem.
-Presents the scientific assumption or hypothesis we aim to test.
-Explains what makes the approach or idea novel compared to existing work
-Summarizes the proposed solution and how it will be carried out.
-States the anticipated results and how success will be evaluated.

WRITING INSTRUCTIONS:
-Before each paragraph, provide a comment (using %) that clearly states the purpose of the paragraph and what content will be covered.
-Use bold, italic, or any other special text formatting to emphasize important terms, core concepts, or notable findings.
-Ensure a smooth narrative flow: each paragraph should connect logically and cohesively with the content from previous sections or subsections.
-Aim for clarity and consistency so that readers can easily follow the progression of the document and understand how each part contributes to the overall message or structure.
-Ensure the tone is formal, precise, and suitable for an academic audience.
-Do not add any citations as reference. 

Respond in the following format:

<tex_START>
<LATEX>
<tex_FINISH>

In <LATEX>, provide the response for the Introduction Section. Start with \section{{Introduction}} and then write the section content.
"""

writer_methods_prompt = """You are given the following document:

Document:
{document}

We have already implemented the idea and collected the results. Below is a description of the workflow we followed to obtain those results:

Notes:
{notes}

The following shows the latest code used for implementation:

Code:
{code}

The following is the list of tools we had access to during the research 

Tools:
{tools}

The following constraints were also imposed

Constraints:
{constraints}

Your TASK:
- Carefully analyze the document, the workflow notes, the code, tools, and constraints.
- Write a detailed, structured, and well-reasoned document in **LATEX format**.
- The goal is to create a comprehensive **Methods** section that explains in depth how the idea was implemented.
- Focus exclusively on the **methodology** — do not report any results.

WRITING STRATEGY:
The Methods section should cover the following aspects
- Reiterates the motivation behind the experiments.
- Discusses in detail the design rationale and parameter selection.
- Discusses in high-level of detail the implementation strategy.
- Discusses the execution workflow, automation, and reproducability. 
- Mentions challenges and considerations.
- This section does not discuss the visual plots and tables (this is the scope of Results section)
- Be exhaustive in your response. There is no length limit in response length.


WRITING INSTRUCTIONS:
-Before each paragraph, provide a comment (using %)  that clearly states the purpose of the paragraph and what content will be covered.
-Use bold, italic, or any other special text formatting to emphasize important terms, core concepts, or notable findings.
-Ensure a smooth narrative flow: each paragraph should connect logically and cohesively with the content from previous sections or subsections.
-Aim for clarity and consistency so that readers can easily follow the progression of the document and understand how each part contributes to the overall message or structure.
-Ensure the tone is formal, precise, and suitable for an academic audience.
- Do not make up things you are unsure about. Only include information you are certain of and that is explicitly stated in the prompt. This helps prevent hallucinations and inaccurate informtion in the report.

IMPORTANT:
- The results may have been collected in several rounds. You need to make this clear and provide details.
- The full workflow is provided in Notes. You must carefully read it and put all the details in your response.

Respond in the following format:

<tex_START>
<LATEX>
<tex_FINISH>

In <LATEX>, provide the response for the Methods Section. Start with \section{{Methods}} and then write the section content.
"""

writer_results_prompt = """You are given the following document:

Document:
{document}

We have already implemented the idea and collected the results. Below is a description of the workflow we followed to obtain those results:

Notes:
{notes}

The final results are as follows:
{final_results}

The following plots have been generated. Each plot name is followed by a dictionary consisting description, hypothesis_shift, novel_patterns, new_hypothesis, mechanistic_speculation, implications, and caption

Plots:
{plots}

Here are the fitting parameters from the regression
{regression}

Your TASK:
- Carefully analyze the document, the workflow notes, the plots with all the details, and regression parameters (if available).
- Write a detailed, structured, and well-reasoned document in **LATEX format**.
- The goal is to produce a comprehensive overemphasized **Results** section that analyzes and contextualizes the findings of the research.

WRITING STRATEGY:
The results sections should carefully cover the following aspects with focus on completeness: 
- Before representing the results, briefly restates the motivation.
- Shows the results. Explains the motivation behind this result. Discusses the results with overemphasize level of detail.
- Discusses mechanistic insights behind the results, mechanisms.
- Highlights the core findings of the results. 
- Analyzes whether the findings support, refine, or contradict the original hypothesis.
- Discusses the limitation of the method.

WRITING INSTRUCTIONS:
- The paragraphs devoted to results are very crucial to show the strength and impact of the work. As such, you need to pay much attention to clarity, completeness, and accuracy.
-Before each paragraph, provide a comment (using %)  that clearly states the purpose of the paragraph and what content will be covered.
-Use bold, italic, or any other special text formatting to emphasize important terms, core concepts, or notable findings.
-Ensure a smooth narrative flow: each paragraph should connect logically and cohesively with the content from previous sections or subsections.
-Aim for clarity and consistency so that readers can easily follow the progression of the document and understand how each part contributes to the overall message or structure.
-Ensure the tone is formal, precise, and suitable for an academic audience.
- Do not make up things you are unsure about. Only include information you are certain of and that is explicitly stated in the prompt. This helps prevent hallucinations and inaccurate informtion in the report.
- Be exhaustive in your response. There is no length limit in response length.


MUSTS for PLOTS:
- You should include all the plots mentioned above in the text. It is important that the caption you create fully explains the figure, like the one provided for you.
- The images should be placed, labled, and referred accurately in the text. 
- Devote a specific subsection/paragraph for each plot. In this subsection/paragraph, you should include the plot description, patterns, and mechanistic explanation of the trend and behavior, and implications. Include any other aspect that you find relevant to the research. 
- Use starting statement that gives the overall objective and ending statement that gives a brief summary.

- Use the following format to insert images: 
\begin{{figure}}[h] \centering
\includegraphics[width=0.8\textwidth]{{example-image.png}} % Replace with your image file
\caption{{An example image}}
\label{{fig:example}}
\end{{figure}}

MUST for TABLES:
-Although there might be no table in the results, you are highly encouraged to design and insert tables in your response.
-Target tables that facilitate data analysis and impact, such as statisitcal values, fitting parameteres, or any other aspect you find revelant to the research.
-The tables should be placed, labled, and referred accurately in your response.
- Use the following format to insert tables: 
\begin{{table}}[h]
    \centering
    \begin{{tabular}}{{|c|c|c|}}
...
    \end{{tabular}}
    \caption{{An example table}}
    \label{{tab:example}}
\end{{table}}

Respond in the following format:

<tex_START>
<LATEX>
<tex_FINISH>

In <LATEX>, provide the response for the Results Section. Start with \section{{Results}} and then write the section content.

"""
writer_conclusion_prompt = """You are given the following document:

Document:
{document}

which originates from the a research conducted for the following query (research goal)
{query}

Your TASK:
- Carefully analyze the document, including the initial research question, the methodological approach, and the results obtained.
- Write a detailed, structured, and well-reasoned document in **LATEX format**.
- The goal is to produce a comprehensive **Conclusion** section.
- Choose a proper title for the research that best reflects its objective.

WRITING STRATEGY:
The Conclusion sections should cover the following aspects: 
- Brief recap of the entire paper. 
- Lists in bullet points the main conclusions from the paper in sholar tone.
- Emphasizes the scientific impact of the findings.
- Emphasizes the broader impact.
- Identifies and discusses notable potential limitations.

WRITING INSTRUCTIONS:
-Before each paragraph, provide a comment (using %)  that clearly states the purpose of the paragraph and what content will be covered.
-Use bold, italic, or any other special text formatting to emphasize important terms, core concepts, or notable findings.
-Ensure a smooth narrative flow: each paragraph should connect logically and cohesively with the content from previous sections or subsections.
-Aim for clarity and consistency so that readers can easily follow the progression of the document and understand how each part contributes to the overall message or structure.
-Ensure the tone is formal, precise, and suitable for an academic audience.
- Be exhaustive in your response. There is no length limit in response length.

Respond in the following format:

<tex_START>
<LATEX>
<tex_FINISH>

In <LATEX>, provide the response for the title and Conclusion Section. Start with \title{{Title}} (where Title is the title), then \section{{Conclusion}} and then write the section content.

"""

writer_outlook_prompt = """You are given the following document:

Document:
{document}

which originated from the following query (research goal)
{query}

Your TASK:
- Carefully analyze the qyery and the entire document
- Write a detailed, structured, and well-reasoned document in **LATEX format**.
- The goal is to produce a comprehensive **Future Work** section.

WRITING STRETEGY:
The Future work sections should cover the following aspects: 
- Identifies open questions, limitations, or challenges encountered during the study that warrant further investigation.
- Proposes specific future experiments, simulations, or theoretical developments that could extend the current findings.
- Highlights new hypotheses, directions, or domains of application inspired by the results.
- Suggests methodological improvements or alternative approaches that could improve performance, accuracy, or generalizability.
- Most impactful scientifi questions to be investigated (see below).
- Suggest new tools to be devloped and how they can address current limitations or open new directions.
- Explain, How AI, specially generative AI such as LLMs can be used in future work.
- Discusses how the future work could address broader scientific questions or be integrated into larger research agendas.
- Be exhaustive in your response. There is no length limit in response length.


GENERAL INSTRUCTIONS:
-Before each paragraph, provide a comment that clearly states the purpose of the paragraph and what content will be covered.
-Use bold, italic, or any other special text formatting to emphasize important terms, core concepts, or notable findings.
-Ensure a smooth narrative flow: each paragraph should connect logically and cohesively with the content from previous sections or subsections.
-Aim for clarity and consistency so that readers can easily follow the progression of the document and understand how each part contributes to the overall message or structure.
-Ensure the tone is formal, precise, and suitable for an academic audience.


INSTRUCTIONS for New Hypothesis Development:
-You need to propose new hypotehses as foundations for future research that address the overall research goal.
-You are encouraged to propose ideas that are inspired by or build upon the current research hypothesis.
-Your goal is to think beyond the original hypothesis and -Prioritize ideas that explore **unseen, creative regions** of the hypothesis space.
-You are encouraged to use other tools to explore novel directions. 

TOOLS:
{tools}

INSTRUCTIONS for MOST IMPACTFUL SCIENTIFIC QUESTIONS:
- Within the provided document, identify the most impactful scientific questions that can be investigated (a) in vitro and (b) in silico. 
- Outline key steps to set up and conduct such investigation, with details and include uniques aspects of the planned work. 

INSTRUCTIONS for NEW tools and function development:
- You need to suggest new tools and functions to be developed for future research.
- Discuss how these tools can open up new avenues for research in the field, or address the limitations of the current research and methods.

INSTRUCTIONS for AI applications:
- Discuss how AI model such as machine learning and deep learning modesl can be used in future research. 
- How advanced generative AI such as LLMs and LLM-driven multi-agent systems can be used to advance the field. 

Respond in the following format:

<tex_START>
<LATEX>
<tex_FINISH>

In <LATEX>, provide the response for the Future Work Section. Start with \section{{Future Work}} and then write the section content.
"""


writer_reflection_prompt = """Closely investigate the response in latex that was just created. The response is a **draft** that requires further elaboration, refinement, and detailed analysis.

Your TASK:
- Carefully examine the previously generated response.
- Revise the response by incorporating significantly more detail, depth, and specificity across all sections.
- Your goal is to produce a substantially **expanded and enriched** version of the documentation, suitable for a rigorous scientific report or publication.
- Ensure the code is free from latex syntax errors. Also, ensure the special characters and latin alphabets are defined inside $$, e.g. $\beta$.

WRITING INSTRUCTIONS:
In writing each section and/or paragraph, you should carefull address the following aspects:
-Before each paragraph, provide a comment (using %)  that clearly states the purpose of the paragraph and what content will be covered.
-Use bold, italic, or any other special text formatting to emphasize important terms, core concepts, or notable findings.
-Ensure a smooth narrative flow: each paragraph should connect logically and cohesively with the content from previous sections or subsections.
-Aim for clarity and consistency so that readers can easily follow the progression of the document and understand how each part contributes to the overall message or structure.
-Ensure the tone is formal, precise, and suitable for an academic audience.


INSTRUCTIONS FOR KEY TAKEAWAYS:
- At anapproprtiate position of each major section or subsection, create a highlight box titled "Key Takeaways".
- The box should include 3–5 concise bullet points summarizing the most important insights, conclusions, or implications from that section.
- Each bullet point should be short, self-contained, and written in a way that is easily understandable to a broader audience.
- The tone should be neutral, informative, and suitable for a scholarly or expert commentary.
- The following latex sample shows how to define and insert the takeaways

\begin{{takeawaybox}}
\begin{{itemize}}
  \item \textbf{{Framing}}: This study addresses a gap in multiscale modeling for alloys.
  \item \textbf{{Motivation}}: Previous methods lacked interpretability and generalization.
  \item \textbf{{Scope}}: We propose a new AI-driven framework to bridge these limitations.
\end{{itemize}}
\end{{takeawaybox}}

Respond in the following format:

THOUGHT:
<THOUGHT>

In <THOUGHT>, provide your feedback, discussing potential issues and ways to improve.

<tex_START>
<LATEX>
<tex_FINISH>

In <LATEX>, provide the refined response for the Section, ensuring high-level detail, critical depth, and insight. Start with \section{{Section Name}} where Section Name is the section name and then write the corresponging section content.
For the Conclusion section, include the title as well (i.e. Start with \title{{Title}} and then \section{{Conclusion}})
"""

