# -*- coding: utf-8 -*-
"""Latex_docs_parser_summarizer.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1m5NNdx3nD7P7SzaQWOYV6Mo2pgod7Tz2

# Installation of required libraries
"""

! pip install pylatexenc
! pip install transformers                               
# sentencepiece library for t5 transformers
! pip install sentencepiece
! pip install sumy

"""# class:LatexParser"""

import re
from pylatexenc.latexwalker import LatexWalker, LatexEnvironmentNode
from pylatexenc.latex2text import LatexNodes2Text


def find_substring(s, start_string, end_string):
    start = s.find(start_string) + len(start_string)
    end = s.find(end_string)
    substring = s[start:end]
    return substring

class LatexTextParser:

    def __init__(self, file_path):
        self.file_path = file_path
        latex_file_list = open(file_path).readlines()
        latex_file_wo_comments = []
        # removal of comments in the latex files
        for line in latex_file_list:
            if not line.startswith("%"):
                latex_file_wo_comments.append(line)
        self.latex_text_wo_comments = "".join(latex_file_wo_comments)

    @staticmethod
    def latex_extract_abstract_sections(latex_text_cleaned):
        abstract = re.findall(r'\\begin{abstract}(.*?)\\end{abstract}', latex_text_cleaned, re.S)
        section_names = re.findall(r'\\section{(.*?)}', latex_text_cleaned, re.S)
        return abstract, section_names

    @staticmethod
    def get_sections_abstract_text(abstract, section_names, latex_text_cleaned):
        section_content = dict()
        sections_tags = []
        for section in section_names:
            section_tag = "\section{" + section + "}"
            sections_tags.append(section_tag)

        sections_tags.append("\end{document}")

        for section_index in range(len(sections_tags) - 1):
            sections_text_latex = find_substring(latex_text_cleaned, sections_tags[section_index],
                                                 sections_tags[section_index + 1])
            sections_text = LatexNodes2Text().latex_to_text(sections_text_latex)
            section_content[section_names[section_index]] = sections_text

        abstract_text = LatexNodes2Text().latex_to_text("".join(abstract))
        section_content['abstract'] = abstract_text
        return section_content

    def latex_text_pre_processing(self):
        figure_content = re.findall(r'\\begin{figure}(.*?)\\end{figure}', self.latex_text_wo_comments, re.S)
        equation_content = re.findall(r'\\begin{equation}(.*?)\\end{equation}', self.latex_text_wo_comments, re.S)
        table_content = re.findall(r'\\begin{table}(.*?)\\end{table}', self.latex_text_wo_comments, re.S)
        latex_codes = table_content + equation_content + figure_content
        latex_text_cleaned = self.latex_text_wo_comments
        for latex_code in latex_codes:
            latex_text_cleaned = latex_text_cleaned.replace(latex_code, "")
        return latex_text_cleaned

    def latex_text_parser(self):
        latex_text_cleaned = self.latex_text_pre_processing()
        abstract, section_names = self.latex_extract_abstract_sections(latex_text_cleaned)
        section_content = self.get_sections_abstract_text(abstract, section_names, latex_text_cleaned)
        return section_content, abstract, section_names

"""# class:TextSummarizer"""

import torch
import sumy
import gensim
from gensim.summarization import summarize
import nltk
import re
nltk.download('punkt')
from transformers import BartForConditionalGeneration, BartTokenizer, BartConfig,BartModel
from transformers import XLMWithLMHeadModel, XLMTokenizer
from transformers import T5Tokenizer, T5Config, T5ForConditionalGeneration
from transformers import BigBirdPegasusForConditionalGeneration, AutoTokenizer
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
from bs4 import BeautifulSoup 
# Import the LexRank summarizer
from sumy.summarizers.lex_rank import LexRankSummarizer
# Importing the parser and tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
# Import the LexRank summarizer
from sumy.summarizers.lex_rank import LexRankSummarizer
lex_rank_summarizer = LexRankSummarizer() 
from sumy.summarizers.lsa import LsaSummarizer
lsa_summarizer=LsaSummarizer()
# Parsing the text string using PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser


class TextSummarizer:
  def __init__(self):
    # Instantiating the model and tokenizer bart
    self.tokenizer_bart=BartTokenizer.from_pretrained('facebook/bart-large-cnn')
    self.model_bart=BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')
    # Instantiating the model and tokenizer t5
    self.model_t5 = T5ForConditionalGeneration.from_pretrained('t5-small')
    self.tokenizer_t5 = T5Tokenizer.from_pretrained('t5-small')
    # Instantiating the model and tokenizer google_bigbird
    self.model_BigBird = BigBirdPegasusForConditionalGeneration.from_pretrained("google/bigbird-pegasus-large-arxiv", attention_type="original_full")
    self.tokenizer_BigBird = AutoTokenizer.from_pretrained("google/bigbird-pegasus-large-arxiv")
    # by default encoder-attention is `block_sparse` with num_random_blocks=3, block_size=64
    
    self.tokenizer_Pegasus = PegasusTokenizer.from_pretrained('google/pegasus-xsum')
    self.model_Pegasus = PegasusForConditionalGeneration.from_pretrained('google/pegasus-xsum')


  def text_summarizer(self, text, min_len, max_len,num_sentences ):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    text_summary_dict = {}

    text_summary_dict['_text_'] = text
    # Encoding the inputs and passing them to model.generate()
    inputs = self.tokenizer_bart.batch_encode_plus([text],return_tensors='pt',truncation=True)
    summary_ids = self.model_bart.generate(inputs['input_ids'], early_stopping=True,min_length = min_len, max_length=max_len)
    bart_summary = self.tokenizer_bart.decode(summary_ids[0], skip_special_tokens=True)
    # print(bart_summary)
    text_summary_dict['bart_summary'] = bart_summary

    inputs = self.tokenizer_BigBird(text, return_tensors='pt')
    summary_ids = self.model_BigBird.generate(**inputs,min_length=min_len, max_length=max_len)
    summary_BigBird = self.tokenizer_BigBird.batch_decode(summary_ids, skip_special_tokens=True)
    text_summary_dict['summary_BigBird'] = summary_BigBird
    print(summary_BigBird)

    # google pegasus summarization

    inputs = self.tokenizer_Pegasus([text], truncation=True, padding='longest', return_tensors="pt")
    summary_ids = self.model_Pegasus.generate(inputs['input_ids'], min_length=min_len, max_length=max_len)
    summary_google_pegasus = self.tokenizer_Pegasus.batch_decode(summary_ids, skip_special_tokens=True)
    text_summary_dict['summary_google_pegasus'] = summary_google_pegasus
    
    t5_text = "summarize:" + text
    # encoding the input text
    input_ids=self.tokenizer_t5.encode(t5_text, return_tensors='pt')
    summary_ids = self.model_t5.generate(input_ids,early_stopping=True, min_length = min_len, max_length=max_len)
    t5_summary = self.tokenizer_t5.decode(summary_ids[0], skip_special_tokens=True)
    text_summary_dict['t5_summary'] = t5_summary
    # gensim_summary
    summary_genensim = summarize(text)
    text_summary_dict['gensim_summary'] = summary_genensim
    my_parser = PlaintextParser.from_string(text,Tokenizer('english'))
    lexrank_summary_sentences = lex_rank_summarizer(my_parser.document,sentences_count=num_sentences)
    lexrank_summary = ""
    for sentence in lexrank_summary_sentences:
      lexrank_summary= lexrank_summary + " "+ str(sentence)
    text_summary_dict['lexrank_summary'] = lexrank_summary
    # creating the lsa summarizer
    parser=PlaintextParser.from_string(text,Tokenizer('english'))
    lsa_summary_sentences= lsa_summarizer(parser.document,num_sentences)
    lsa_summary =""
    #  lsa summary
    for sentence in lsa_summary_sentences:
        lsa_summary= lsa_summary+" "+ str(sentence)
    text_summary_dict['lsa_summary'] = lsa_summary
    return text_summary_dict

textSummarizer = TextSummarizer()

file_path = r"/content/drive/MyDrive/TextSummarizationResults/main.tex"

latex_text_parser = LatexTextParser(file_path)
section_content_file, abstract_file, section_names_file = latex_text_parser.latex_text_parser()

section_names_file

text_summary_dict = dict()
for sections in section_names_file:
  text_summary_dict[sections] = textSummarizer.text_summarizer(section_content_file[sections],100,150,4)

text_summary_dict

file_path_latext_file2 = "/content/drive/MyDrive/TextSummarizationResults/Paper2/main.tex"

file_path_latext_file3 = "/content/drive/MyDrive/TextSummarizationResults/Paper3/sbse_paper.tex"

def latex_parser_summarizer(file_path):
  latex_text_parser = LatexTextParser(file_path)
  section_content_file, abstract_file, section_names_file = latex_text_parser.latex_text_parser()
  text_summary_dict = dict()
  for sections in section_names_file:
    text_summary_dict[sections] = textSummarizer.text_summarizer(section_content_file[sections],100,150,4)
  return text_summary_dict

text_summary_dict_file2 = latex_parser_summarizer(file_path_latext_file2)

text_summary_dict_file3 = latex_parser_summarizer(file_path_latext_file3)

## Dumping the result into json files
save_file_path = r"/content/drive/MyDrive/TextSummarizationResults/summary_section_results_sbse.json"
import json
with open(save_file_path, 'w') as fp:
    json.dump(text_summary_dict_file3, fp, indent=4)

## Dumping the result into json files
save_file_path = r"/content/drive/MyDrive/TextSummarizationResults/summary_section_results_file2.json"
import json
with open(save_file_path, 'w') as fp:
    json.dump(text_summary_dict_file2, fp, indent=4)

text_summary_dict_file3

